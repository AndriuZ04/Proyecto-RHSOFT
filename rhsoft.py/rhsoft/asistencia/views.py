import json
from datetime import date, datetime, timedelta

from django.http  import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth

from .models import Empleado, Persona, Cargo, Departamento, Contrato, Registro, SstAccidente, CargoDia


# ── Helpers de sesión ────────────────────────────────────────────

def get_empleado_sesion(request):
    """Retorna el empleado de la sesión o None."""
    emp_id = request.session.get('empleado_id')
    if not emp_id:
        return None
    try:
        return Empleado.objects.select_related('ID_Persona', 'ID_Cargo',
                                               'ID_Cargo__ID_Departamento').get(pk=emp_id)
    except Empleado.DoesNotExist:
        return None


def login_required_view(view_func):
    """Decorador simple: redirige a login si no hay sesión."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('empleado_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required_view(view_func):
    """Decorador: requiere rol admin."""
    def wrapper(request, *args, **kwargs):
        if request.session.get('rol') != 'admin':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════════════════════════
#  LOGIN / LOGOUT  (index.php → login)
# ══════════════════════════════════════════════════════════════════

def login_view(request):
    """Pantalla de login con PIN."""
    # Cerrar sesión
    if request.GET.get('logout'):
        request.session.flush()
        return redirect('login')

    error = None

    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        try:
            emp = Empleado.objects.select_related('ID_Persona').get(
                PIN=pin, Estado_Empleado='Activo'
            )
            request.session['empleado_id'] = emp.ID_Empleado
            request.session['nombre']      = emp.nombre_completo
            request.session['rol']         = emp.Rol

            if emp.Rol == 'admin':
                return redirect('admin_panel')
            return redirect('registro')

        except Empleado.DoesNotExist:
            error = 'PIN incorrecto o empleado inactivo.'

    return render(request, 'asistencia/login.html', {'error': error})


# ══════════════════════════════════════════════════════════════════
#  REGISTRO DE ASISTENCIA  (registro.php → registro)
# ══════════════════════════════════════════════════════════════════

@login_required_view
def registro_view(request):
    """Vista de marcación de entrada/salida."""
    emp = get_empleado_sesion(request)
    hoy = date.today()

    # ── AJAX: entrada / salida ────────────────────────────────────
    if request.method == 'POST' and request.POST.get('accion'):
        accion = request.POST['accion']

        if accion == 'entrada':
            # R18: no duplicar si ya hay entrada sin salida
            if Registro.objects.filter(ID_Empleado=emp, Fecha=hoy, Hora_Salida__isnull=True).exists():
                return JsonResponse({'ok': False, 'msg': 'Ya tienes una entrada activa hoy.'})
            if Registro.objects.filter(ID_Empleado=emp, Fecha=hoy, Hora_Salida__isnull=False).exists():
                return JsonResponse({'ok': False, 'msg': 'Ya completaste tu jornada de hoy.'})

            ahora = datetime.now().time()
            Registro.objects.create(
                ID_Empleado=emp,
                Fecha=hoy,
                Hora_Entrada=ahora,
                Tipo='Normal'
            )
            return JsonResponse({'ok': True, 'hora': ahora.strftime('%H:%M:%S'),
                                 'msg': '¡Entrada registrada con éxito!'})

        if accion == 'salida':
            reg = Registro.objects.filter(
                ID_Empleado=emp, Fecha=hoy, Hora_Salida__isnull=True
            ).first()
            if not reg:
                return JsonResponse({'ok': False, 'msg': 'No hay entrada activa para registrar salida.'})

            ahora = datetime.now().time()
            reg.Hora_Salida = ahora
            reg.save()
            return JsonResponse({'ok': True, 'hora': ahora.strftime('%H:%M:%S'),
                                 'msg': '¡Salida registrada con éxito!'})

        return JsonResponse({'ok': False, 'msg': 'Acción no reconocida.'})

    # ── Datos del empleado ────────────────────────────────────────
    cargo = emp.ID_Cargo

    # R13: contrato vigente
    contrato_vigente = Contrato.objects.filter(
        ID_Empleado=emp, Estado_Contrato='Vigente'
    ).order_by('-Fecha_Inicio').first()

    # R17: días laborales del cargo
    ORDEN_DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_qs = CargoDia.objects.filter(ID_Cargo=cargo).values_list('Dia_Semana', flat=True)
    dias_laborales = sorted(list(dias_qs), key=lambda d: ORDEN_DIAS.index(d) if d in ORDEN_DIAS else 99)

    # Estado de hoy
    registro_hoy  = Registro.objects.filter(ID_Empleado=emp, Fecha=hoy).order_by('-ID_Registro').first()
    hay_entrada   = bool(registro_hoy and registro_hoy.Hora_Entrada)
    hay_salida    = bool(registro_hoy and registro_hoy.Hora_Salida)

    # Historial (30 últimos)
    historial = Registro.objects.filter(ID_Empleado=emp).order_by('-Fecha', '-Hora_Entrada')[:30]

    # Estadísticas del mes
    mes_inicio = hoy.replace(day=1)
    regs_mes   = Registro.objects.filter(ID_Empleado=emp, Fecha__gte=mes_inicio)
    total_dias = regs_mes.count()
    dias_completos = regs_mes.filter(Hora_Salida__isnull=False).count()

    # Promedio de horas (calculado en Python)
    promedio_horas = None
    duraciones = []
    for r in regs_mes.filter(Hora_Salida__isnull=False):
        entrada = datetime.combine(r.Fecha, r.Hora_Entrada)
        salida  = datetime.combine(r.Fecha, r.Hora_Salida)
        duraciones.append((salida - entrada).seconds)
    if duraciones:
        avg_seg = sum(duraciones) // len(duraciones)
        h, resto = divmod(avg_seg, 3600)
        m = resto // 60
        promedio_horas = f'{h:02d}:{m:02d}'

    # Duración de la jornada de hoy (si está completa)
    duracion_hoy = None
    if hay_entrada and hay_salida:
        entrada = datetime.combine(hoy, registro_hoy.Hora_Entrada)
        salida  = datetime.combine(hoy, registro_hoy.Hora_Salida)
        seg = (salida - entrada).seconds
        h, r = divmod(seg, 3600)
        duracion_hoy = f'{h:02d}:{r // 60:02d}h'

    # Historial con duraciones calculadas
    historial_con_dur = []
    for r in historial:
        dur = None
        if r.Hora_Entrada and r.Hora_Salida:
            e = datetime.combine(r.Fecha, r.Hora_Entrada)
            s = datetime.combine(r.Fecha, r.Hora_Salida)
            seg = (s - e).seconds
            hh, rr = divmod(seg, 3600)
            dur = f'{hh:02d}:{rr // 60:02d}h'
        historial_con_dur.append({'reg': r, 'duracion': dur})

    ctx = {
        'emp':              emp,
        'cargo':            cargo,
        'departamento':     cargo.ID_Departamento,
        'contrato_vigente': contrato_vigente,
        'dias_laborales':   dias_laborales,
        'registro_hoy':     registro_hoy,
        'hay_entrada':      hay_entrada,
        'hay_salida':       hay_salida,
        'duracion_hoy':     duracion_hoy,
        'historial':        historial_con_dur,
        'total_dias':       total_dias,
        'dias_completos':   dias_completos,
        'promedio_horas':   promedio_horas,
        'hoy':              hoy,
        'nombre':           request.session.get('nombre'),
        'rol':              request.session.get('rol'),
    }
    return render(request, 'asistencia/registro.html', ctx)


# ══════════════════════════════════════════════════════════════════
#  PANEL DE ADMINISTRACIÓN  (admin.php → admin_panel)
# ══════════════════════════════════════════════════════════════════

@admin_required_view
def admin_view(request):
    """Panel de administración."""

    # ── AJAX POST ────────────────────────────────────────────────
    if request.method == 'POST' and request.POST.get('accion'):
        accion = request.POST['accion']

        # ── Guardar / actualizar empleado ─────────────────────────
        if accion == 'guardar_empleado':
            try:
                with transaction.atomic():
                    persona_id = int(request.POST.get('ID_Persona', 0) or 0)
                    emp_id     = int(request.POST.get('ID_Empleado', 0) or 0)

                    datos_persona = {
                        'Numero_Documento': request.POST['Numero_Documento'],
                        'Nombres':          request.POST['Nombres'],
                        'Apellidos':        request.POST['Apellidos'],
                        'Email':            request.POST.get('Email') or None,
                        'Telefono':         request.POST.get('Telefono') or None,
                        'Fecha_Nacimiento': request.POST.get('Fecha_Nacimiento') or None,
                    }

                    if persona_id:
                        Persona.objects.filter(pk=persona_id).update(**datos_persona)
                        persona = Persona.objects.get(pk=persona_id)
                    else:
                        persona = Persona.objects.create(**datos_persona)

                    pin = request.POST['PIN']
                    # Validar PIN único
                    qs_pin = Empleado.objects.filter(PIN=pin)
                    if emp_id:
                        qs_pin = qs_pin.exclude(pk=emp_id)
                    if qs_pin.exists():
                        return JsonResponse({'ok': False, 'msg': 'El PIN ya está en uso por otro empleado.'})

                    datos_emp = {
                        'ID_Cargo_id':      int(request.POST['ID_Cargo']),
                        'PIN':              pin,
                        'Rol':              request.POST.get('Rol', 'empleado'),
                        'Fecha_Ingreso':    request.POST.get('Fecha_Ingreso') or None,
                        'Fecha_Retiro':     request.POST.get('Fecha_Retiro') or None,
                        'Estado_Empleado':  request.POST.get('Estado_Empleado', 'Activo'),
                    }

                    if emp_id:
                        Empleado.objects.filter(pk=emp_id).update(**datos_emp)
                    else:
                        datos_emp['ID_Persona'] = persona
                        emp = Empleado.objects.create(**datos_emp)

                        # R13: crear contrato automático
                        tipo = request.POST.get('Tipo_Contrato')
                        f_inicio = request.POST.get('Fecha_Inicio_Contrato')
                        if tipo and f_inicio:
                            Contrato.objects.create(
                                ID_Empleado=emp,
                                ID_Cargo_id=int(request.POST['ID_Cargo']),
                                Tipo_Contrato=tipo,
                                Salario_Pactado=request.POST.get('Salario_Pactado') or None,
                                Fecha_Inicio=f_inicio,
                                Fecha_Fin=request.POST.get('Fecha_Fin_Contrato') or None,
                                Estado_Contrato='Vigente',
                            )

                return JsonResponse({'ok': True, 'msg': 'Empleado guardado correctamente.'})
            except Exception as e:
                msg = 'El número de documento ya existe.' if 'UK_Numero_Documento' in str(e) else f'Error: {e}'
                return JsonResponse({'ok': False, 'msg': msg})

        # ── R13: Guardar contrato ─────────────────────────────────
        if accion == 'guardar_contrato':
            try:
                contrato_id = int(request.POST.get('ID_Contrato', 0) or 0)
                datos = {
                    'Tipo_Contrato':   request.POST.get('Tipo_Contrato'),
                    'Salario_Pactado': request.POST.get('Salario_Pactado') or None,
                    'Fecha_Inicio':    request.POST.get('Fecha_Inicio'),
                    'Fecha_Fin':       request.POST.get('Fecha_Fin') or None,
                    'Estado_Contrato': request.POST.get('Estado_Contrato', 'Vigente'),
                }
                if contrato_id:
                    Contrato.objects.filter(pk=contrato_id).update(**datos)
                else:
                    datos['ID_Empleado_id'] = int(request.POST['ID_Empleado'])
                    datos['ID_Cargo_id']    = int(request.POST['ID_Cargo'])
                    Contrato.objects.create(**datos)
                return JsonResponse({'ok': True, 'msg': 'Contrato guardado correctamente.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        # ── R14: Guardar accidente SST ────────────────────────────
        if accion == 'guardar_sst':
            try:
                sst_id = int(request.POST.get('ID_Accidente', 0) or 0)
                datos = {
                    'ID_Empleado_id':  int(request.POST['ID_Empleado_SST']),
                    'Fecha_Accidente': request.POST.get('Fecha_Accidente'),
                    'Tipo_Accidente':  request.POST.get('Tipo_Accidente'),
                    'Descripcion':     request.POST.get('Descripcion'),
                    'Accion_Inmediata':request.POST.get('Accion_Inmediata') or None,
                    'Fecha_Reporte':   request.POST.get('Fecha_Reporte') or None,
                }
                if sst_id:
                    SstAccidente.objects.filter(pk=sst_id).update(**datos)
                else:
                    SstAccidente.objects.create(**datos)
                return JsonResponse({'ok': True, 'msg': 'Accidente SST registrado correctamente.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        # ── Get contratos de empleado ─────────────────────────────
        if accion == 'get_contratos':
            contratos = list(
                Contrato.objects.filter(ID_Empleado_id=int(request.POST['ID_Empleado']))
                .order_by('-Fecha_Inicio')
                .values('ID_Contrato', 'Tipo_Contrato', 'Salario_Pactado',
                        'Fecha_Inicio', 'Fecha_Fin', 'Estado_Contrato')
            )
            # Convertir decimals y fechas a string para JSON
            for c in contratos:
                c['Salario_Pactado'] = float(c['Salario_Pactado']) if c['Salario_Pactado'] else None
                c['Fecha_Inicio']    = str(c['Fecha_Inicio'])    if c['Fecha_Inicio']    else None
                c['Fecha_Fin']       = str(c['Fecha_Fin'])       if c['Fecha_Fin']       else None
            return JsonResponse(contratos, safe=False)

        # ── Get accidentes SST ────────────────────────────────────
        if accion == 'get_sst':
            accidentes = list(
                SstAccidente.objects.filter(ID_Empleado_id=int(request.POST['ID_Empleado']))
                .order_by('-Fecha_Accidente')
                .values()
            )
            for a in accidentes:
                a['Fecha_Accidente'] = str(a['Fecha_Accidente']) if a['Fecha_Accidente'] else None
                a['Fecha_Reporte']   = str(a['Fecha_Reporte'])   if a['Fecha_Reporte']   else None
            return JsonResponse(accidentes, safe=False)

        # ── Get registros de asistencia ───────────────────────────
        if accion == 'get_registros':
            registros = list(
                Registro.objects.filter(ID_Empleado_id=int(request.POST['ID_Empleado']))
                .order_by('-Fecha', '-Hora_Entrada')
                .values('Fecha', 'Hora_Entrada', 'Hora_Salida', 'Tipo', 'Observacion')[:50]
            )
            for r in registros:
                r['Fecha']       = str(r['Fecha'])
                r['Hora_Entrada']= str(r['Hora_Entrada']) if r['Hora_Entrada'] else None
                r['Hora_Salida'] = str(r['Hora_Salida'])  if r['Hora_Salida']  else None
            return JsonResponse(registros, safe=False)

        # ── Get empleado para editar ──────────────────────────────
        if accion == 'get_empleado':
            try:
                emp = Empleado.objects.select_related('ID_Persona', 'ID_Cargo').get(
                    pk=int(request.POST['ID_Empleado'])
                )
                p = emp.ID_Persona
                data = {
                    'ID_Empleado':      emp.ID_Empleado,
                    'ID_Persona':       p.ID_Persona,
                    'Nombres':          p.Nombres,
                    'Apellidos':        p.Apellidos,
                    'Numero_Documento': p.Numero_Documento,
                    'Email':            p.Email,
                    'Telefono':         p.Telefono,
                    'Fecha_Nacimiento': str(p.Fecha_Nacimiento) if p.Fecha_Nacimiento else None,
                    'ID_Cargo':         emp.ID_Cargo_id,
                    'PIN':              emp.PIN,
                    'Rol':              emp.Rol,
                    'Fecha_Ingreso':    str(emp.Fecha_Ingreso) if emp.Fecha_Ingreso else None,
                    'Fecha_Retiro':     str(emp.Fecha_Retiro)  if emp.Fecha_Retiro  else None,
                    'Estado_Empleado':  emp.Estado_Empleado,
                }
                return JsonResponse(data)
            except Empleado.DoesNotExist:
                return JsonResponse({'ok': False, 'msg': 'Empleado no encontrado.'})

        # ── Cambiar estado ────────────────────────────────────────
        if accion == 'cambiar_estado':
            Empleado.objects.filter(pk=int(request.POST['ID_Empleado'])).update(
                Estado_Empleado=request.POST['estado']
            )
            return JsonResponse({'ok': True})

        # ── R12: Dar de baja ──────────────────────────────────────
        if accion == 'eliminar_empleado':
            try:
                emp = Empleado.objects.get(pk=int(request.POST['ID_Empleado']))
                emp.Estado_Empleado = 'Inactivo'
                emp.Fecha_Retiro    = date.today()
                emp.save()
                Contrato.objects.filter(ID_Empleado=emp, Estado_Contrato='Vigente').update(
                    Estado_Contrato='Terminado', Fecha_Fin=date.today()
                )
                return JsonResponse({'ok': True, 'msg': f'{emp.nombre_completo} dado de baja correctamente.'})
            except Empleado.DoesNotExist:
                return JsonResponse({'ok': False, 'msg': 'Empleado no encontrado.'})

    # ── GET: renderizar panel ─────────────────────────────────────
    empleados = (
        Empleado.objects
        .select_related('ID_Persona', 'ID_Cargo', 'ID_Cargo__ID_Departamento')
        .order_by('ID_Persona__Apellidos')
    )
    cargos       = Cargo.objects.select_related('ID_Departamento').all()
    departamentos = Departamento.objects.all()

    # Estadísticas rápidas
    hoy = date.today()
    presentes_hoy = Registro.objects.filter(Fecha=hoy, Hora_Salida__isnull=True).count()
    total_activos = Empleado.objects.filter(Estado_Empleado='Activo').count()
    accidentes_mes = SstAccidente.objects.filter(
        Fecha_Accidente__gte=hoy.replace(day=1)
    ).count()

    ctx = {
        'empleados':      empleados,
        'cargos':         cargos,
        'departamentos':  departamentos,
        'presentes_hoy':  presentes_hoy,
        'total_activos':  total_activos,
        'accidentes_mes': accidentes_mes,
        'nombre':         request.session.get('nombre'),
    }
    return render(request, 'asistencia/admin.html', ctx)
