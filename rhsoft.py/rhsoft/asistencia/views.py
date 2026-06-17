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
            # R17: verificar que hoy sea día laboral del cargo
            DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            dia_hoy = DIAS_SEMANA[hoy.weekday()]
            dias_cargo = list(CargoDia.objects.filter(
                ID_Cargo=emp.ID_Cargo
            ).values_list('Dia_Semana', flat=True))
            if dias_cargo and dia_hoy not in dias_cargo:
                return JsonResponse({
                    'ok': False,
                    'msg': f'Hoy es {dia_hoy} y no es un día laboral para tu cargo. '
                           f'Días laborales: {", ".join(dias_cargo)}.'
                })

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
                SALARIO_MINIMO = 1750905  # Salario mínimo legal vigente Colombia 2026
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
                        # R13: verificar que empleado activo tenga contrato vigente
                        estado = request.POST.get('Estado_Empleado', 'Activo')
                        if estado == 'Activo':
                            tiene_vigente = Contrato.objects.filter(
                                ID_Empleado_id=emp_id, Estado_Contrato='Vigente'
                            ).exists()
                            if not tiene_vigente:
                                return JsonResponse({
                                    'ok': False,
                                    'msg': 'No se puede dejar un empleado activo sin contrato vigente. Agrega o activa un contrato primero.'
                                })
                    else:
                        datos_emp['ID_Persona'] = persona
                        emp = Empleado.objects.create(**datos_emp)

                        # R13: crear contrato automático
                        tipo = request.POST.get('Tipo_Contrato')
                        f_inicio = request.POST.get('Fecha_Inicio_Contrato')
                        if tipo and f_inicio:
                            sal_ct = request.POST.get('Salario_Pactado')
                            if not sal_ct:
                                raise ValueError('El salario pactado es obligatorio para registrar un contrato.')
                            if float(sal_ct) < SALARIO_MINIMO:
                                raise ValueError(f'El salario pactado no puede ser inferior al salario mínimo (${SALARIO_MINIMO:,.0f}).')
                            Contrato.objects.create(
                                ID_Empleado=emp,
                                ID_Cargo_id=int(request.POST['ID_Cargo']),
                                Tipo_Contrato=tipo,
                                Salario_Pactado=request.POST.get('Salario_Pactado') or None,
                                Fecha_Inicio=f_inicio,
                                Fecha_Fin=request.POST.get('Fecha_Fin_Contrato') or None,
                                Estado_Contrato='Vigente',
                            )
                        elif datos_emp.get('Estado_Empleado') == 'Activo':
                            # R13: bloquear creación de empleado activo sin contrato
                            # Revertimos la transacción usando rollback implícito
                            raise ValueError('Un empleado activo debe tener contrato vigente. Selecciona un tipo de contrato y fecha de inicio.')

                return JsonResponse({'ok': True, 'msg': 'Empleado guardado correctamente.'})
            except ValueError as e:
                return JsonResponse({'ok': False, 'msg': str(e)})
            except Exception as e:
                msg = 'El número de documento ya existe.' if 'Numero_Documento' in str(e) or 'Duplicate' in str(e) else f'Error: {e}'
                return JsonResponse({'ok': False, 'msg': msg})

        # ── R13: Guardar contrato ─────────────────────────────────
        if accion == 'guardar_contrato':
            try:
                contrato_id = int(request.POST.get('ID_Contrato', 0) or 0)
                emp_id = int(request.POST['ID_Empleado'])
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
                    datos['ID_Empleado_id'] = emp_id
                    datos['ID_Cargo_id']    = int(request.POST['ID_Cargo'])
                    Contrato.objects.create(**datos)

                # R13: advertir si el empleado activo quedó sin contrato vigente
                emp_obj = Empleado.objects.get(pk=emp_id)
                if emp_obj.Estado_Empleado == 'Activo':
                    tiene_vigente = Contrato.objects.filter(
                        ID_Empleado=emp_obj, Estado_Contrato='Vigente'
                    ).exists()
                    if not tiene_vigente:
                        return JsonResponse({
                            'ok': False,
                            'msg': 'Este empleado está activo y quedaría sin contrato vigente. Cambia el estado del contrato o añade uno vigente.'
                        })

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

        # ── R16: Guardar cargo con validación de salario mínimo ──────
        if accion == 'guardar_cargo':
            try:
                # Salario mínimo legal vigente Colombia 2026
                SALARIO_MINIMO = 1750905

                salario = request.POST.get('Salario_Base')
                if salario:
                    salario_val = float(salario)
                    if salario_val < SALARIO_MINIMO:
                        return JsonResponse({
                            'ok': False,
                            'msg': f'El salario base (${salario_val:,.0f}) no puede ser inferior al salario mínimo legal vigente (${SALARIO_MINIMO:,.0f}).'
                        })

                cargo_id = int(request.POST.get('ID_Cargo', 0) or 0)
                datos = {
                    'ID_Departamento_id':  int(request.POST['ID_Departamento']),
                    'Nombre_Cargo':        request.POST['Nombre_Cargo'],
                    'Descripcion_Funciones': request.POST.get('Descripcion_Funciones') or None,
                    'Salario_Base':        salario or None,
                    'Hora_Inicio_Jornada': request.POST.get('Hora_Inicio_Jornada') or None,
                    'Hora_Fin_Jornada':    request.POST.get('Hora_Fin_Jornada') or None,
                }
                if cargo_id:
                    Cargo.objects.filter(pk=cargo_id).update(**datos)
                else:
                    Cargo.objects.create(**datos)
                return JsonResponse({'ok': True, 'msg': 'Cargo guardado correctamente.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

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

    contratos  = Contrato.objects.select_related('ID_Empleado__ID_Persona', 'ID_Cargo').order_by('-Fecha_Inicio')
    accidentes = SstAccidente.objects.select_related('ID_Empleado__ID_Persona', 'ID_Empleado__ID_Cargo').order_by('-Fecha_Accidente')

    ctx = {
        'empleados':      empleados,
        'cargos':         cargos,
        'departamentos':  departamentos,
        'presentes_hoy':  presentes_hoy,
        'total_activos':  total_activos,
        'accidentes_mes': accidentes_mes,
        'contratos':      contratos,
        'accidentes':     accidentes,
        'nombre':         request.session.get('nombre'),
    }
    return render(request, 'asistencia/admin.html', ctx)


# ══════════════════════════════════════════════════════════════════
#  PERFIL DEL EMPLEADO
# ══════════════════════════════════════════════════════════════════

@login_required_view
def perfil_view(request):
    emp    = get_empleado_sesion(request)
    persona = emp.ID_Persona
    ok_msg = error = None

    if request.method == 'POST':
        email    = request.POST.get('Email', '').strip() or None
        telefono = request.POST.get('Telefono', '').strip() or None
        Persona.objects.filter(pk=persona.pk).update(Email=email, Telefono=telefono)
        persona.Email    = email
        persona.Telefono = telefono
        ok_msg = 'Perfil actualizado correctamente.'

    contrato_vigente = Contrato.objects.filter(
        ID_Empleado=emp, Estado_Contrato='Vigente'
    ).order_by('-Fecha_Inicio').first()

    ctx = {
        'emp': emp, 'persona': persona,
        'cargo': emp.ID_Cargo,
        'departamento': emp.ID_Cargo.ID_Departamento,
        'contrato_vigente': contrato_vigente,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
        'ok_msg': ok_msg, 'error': error,
    }
    return render(request, 'asistencia/perfil.html', ctx)


# ══════════════════════════════════════════════════════════════════
#  POSTULACIÓN PÚBLICA
# ══════════════════════════════════════════════════════════════════

def postulacion_view(request):
    from .models import Postulacion
    cargos = Cargo.objects.select_related('ID_Departamento').all()
    ok_msg = error = None

    if request.method == 'POST':
        documento  = request.POST.get('Numero_Documento', '').strip()
        nombres    = request.POST.get('Nombres', '').strip()
        apellidos  = request.POST.get('Apellidos', '').strip()
        email      = request.POST.get('Email', '').strip() or None
        telefono   = request.POST.get('Telefono', '').strip() or None
        nacimiento = request.POST.get('Fecha_Nacimiento', '') or None
        cargo_id   = request.POST.get('Cargo_Aspirado')
        hoja_vida  = request.FILES.get('Hoja_Vida')

        if not all([documento, nombres, apellidos, cargo_id, hoja_vida]):
            error = 'Por favor completa todos los campos obligatorios y adjunta tu hoja de vida.'
        elif not hoja_vida.name.endswith('.pdf'):
            error = 'La hoja de vida debe estar en formato PDF.'
        else:
            try:
                persona, _ = Persona.objects.get_or_create(
                    Numero_Documento=documento,
                    defaults={'Nombres': nombres, 'Apellidos': apellidos,
                              'Email': email, 'Telefono': telefono,
                              'Fecha_Nacimiento': nacimiento}
                )
                if Empleado.objects.filter(ID_Persona=persona, Estado_Empleado='Activo').exists():
                    error = 'Ya eres empleado activo de la empresa.'
                elif Postulacion.objects.filter(
                    ID_Persona=persona, Cargo_Aspirado_id=cargo_id,
                    Estado__in=['Pendiente', 'Aceptado', 'Entrevista']
                ).exists():
                    error = 'Ya tienes una postulación activa para ese cargo.'
                else:
                    Postulacion.objects.create(
                        ID_Persona=persona, Cargo_Aspirado_id=cargo_id,
                        Hoja_Vida=hoja_vida, Estado='Pendiente',
                    )
                    ok_msg = f'¡Gracias {nombres}! Tu postulación fue enviada correctamente.'
            except Exception as e:
                error = f'Error al procesar tu postulación: {e}'

    return render(request, 'asistencia/postulacion.html',
                  {'cargos': cargos, 'ok_msg': ok_msg, 'error': error})


# ══════════════════════════════════════════════════════════════════
#  EVALUACIÓN IA DEL CV (R2/R3)
# ══════════════════════════════════════════════════════════════════

@admin_required_view
def evaluar_cv_view(request):
    import json, urllib.request, os
    from .models import Postulacion

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'msg': 'Método no permitido.'})

    post_id = int(request.POST.get('ID_Postulacion', 0))
    try:
        post  = Postulacion.objects.select_related('ID_Persona', 'Cargo_Aspirado').get(pk=post_id)
        cargo = post.Cargo_Aspirado

        # Extraer texto del PDF
        pdf_path = post.Hoja_Vida.path
        texto_cv = ''
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                texto_cv += page.extract_text() or ''
        except Exception:
            texto_cv = '(No se pudo extraer texto del PDF)'

        requisitos = cargo.Requisitos or 'No se han definido requisitos específicos para este cargo.'

        prompt = f"""Eres un evaluador de recursos humanos. Analiza si el siguiente candidato cumple los requisitos del cargo.

CARGO: {cargo.Nombre_Cargo}
DEPARTAMENTO: {cargo.ID_Departamento.Nombre_Departamento}
REQUISITOS DEL CARGO:
{requisitos}

HOJA DE VIDA DEL CANDIDATO:
{texto_cv[:3000]}

Responde ÚNICAMENTE con un JSON con este formato exacto, sin texto adicional:
{{
  "puntaje": <número entre 0 y 100>,
  "cumple": <true o false>,
  "fortalezas": "<texto breve con lo que sí cumple>",
  "debilidades": "<texto breve con lo que no cumple o falta>",
  "recomendacion": "<Apto / No apto / Apto con reservas>"
}}"""

        payload = json.dumps({
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 500,
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode()

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01',
                'x-api-key': os.environ.get('ANTHROPIC_API_KEY', ''),
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        raw = data['content'][0]['text'].strip()
        # Limpiar posibles backticks
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        resultado = json.loads(raw.strip())

        Postulacion.objects.filter(pk=post_id).update(
            Resultado_IA=json.dumps(resultado, ensure_ascii=False),
            Puntaje_IA=resultado.get('puntaje', 0),
        )

        return JsonResponse({'ok': True, 'resultado': resultado})

    except Postulacion.DoesNotExist:
        return JsonResponse({'ok': False, 'msg': 'Postulación no encontrada.'})
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': f'Error al evaluar: {e}'})


# ══════════════════════════════════════════════════════════════════
#  GESTIÓN DE SELECCIÓN (ADMIN)
# ══════════════════════════════════════════════════════════════════

@admin_required_view
def seleccion_view(request):
    from .models import Postulacion

    if request.method == 'POST' and request.POST.get('accion'):
        accion = request.POST['accion']

        if accion == 'cambiar_estado_postulacion':
            try:
                post_id = int(request.POST['ID_Postulacion'])
                Postulacion.objects.filter(pk=post_id).update(
                    Estado=request.POST['Estado'],
                    Observacion=request.POST.get('Observacion', '').strip() or None,
                )
                return JsonResponse({'ok': True, 'msg': f'Estado actualizado a "{request.POST["Estado"]}".'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        if accion == 'contratar':
            try:
                SALARIO_MINIMO = 1750905
                with transaction.atomic():
                    post_id = int(request.POST['ID_Postulacion'])
                    post    = Postulacion.objects.select_related('ID_Persona', 'Cargo_Aspirado').get(pk=post_id)
                    persona = post.ID_Persona

                    if Empleado.objects.filter(ID_Persona=persona, Estado_Empleado='Activo').exists():
                        return JsonResponse({'ok': False, 'msg': 'Esta persona ya es empleado activo.'})

                    pin = request.POST.get('PIN', '').strip()
                    if not pin or len(pin) != 6 or not pin.isdigit():
                        return JsonResponse({'ok': False, 'msg': 'El PIN debe tener exactamente 6 dígitos.'})
                    if Empleado.objects.filter(PIN=pin).exists():
                        return JsonResponse({'ok': False, 'msg': 'Ese PIN ya está en uso.'})

                    sal = request.POST.get('Salario_Pactado', '').strip()
                    if not sal:
                        return JsonResponse({'ok': False, 'msg': 'El salario pactado es obligatorio.'})
                    if float(sal) < SALARIO_MINIMO:
                        return JsonResponse({'ok': False, 'msg': f'El salario no puede ser inferior al mínimo (${SALARIO_MINIMO:,.0f}).'})

                    f_ingreso = request.POST.get('Fecha_Ingreso') or None
                    tipo_ct   = request.POST.get('Tipo_Contrato', 'Indefinido')

                    emp = Empleado.objects.create(
                        ID_Persona=persona, ID_Cargo=post.Cargo_Aspirado,
                        PIN=pin, Rol='empleado',
                        Fecha_Ingreso=f_ingreso, Estado_Empleado='Activo',
                    )
                    Contrato.objects.create(
                        ID_Empleado=emp, ID_Cargo=post.Cargo_Aspirado,
                        Tipo_Contrato=tipo_ct, Salario_Pactado=sal,
                        Fecha_Inicio=f_ingreso, Estado_Contrato='Vigente',
                    )
                    post.Estado = 'Contratado'
                    post.save()

                return JsonResponse({'ok': True, 'msg': f'{persona.Nombres} {persona.Apellidos} fue contratado. PIN: {pin}'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

    from .models import Postulacion
    postulaciones = Postulacion.objects.select_related(
        'ID_Persona', 'Cargo_Aspirado', 'Cargo_Aspirado__ID_Departamento'
    ).order_by('-Fecha_Postulacion')

    ctx = {
        'postulaciones':     postulaciones,
        'total_pendientes':  postulaciones.filter(Estado='Pendiente').count(),
        'total_aceptados':   postulaciones.filter(Estado='Aceptado').count(),
        'total_contratados': postulaciones.filter(Estado='Contratado').count(),
        'total_rechazados':  postulaciones.filter(Estado='Rechazado').count(),
        'nombre':            request.session.get('nombre'),
    }
    return render(request, 'asistencia/seleccion.html', ctx)


# ══════════════════════════════════════════════════════════════════
#  EVALUACIONES DE DESEMPEÑO (R7)
# ══════════════════════════════════════════════════════════════════

@login_required_view
def evaluaciones_view(request):
    from .models import Evaluacion
    rol = request.session.get('rol')
    emp = get_empleado_sesion(request)

    if request.method == 'POST' and rol == 'admin':
        accion = request.POST.get('accion')

        if accion == 'guardar_evaluacion':
            try:
                eval_id  = int(request.POST.get('ID_Evaluacion', 0) or 0)
                datos = {
                    'ID_Empleado_id': int(request.POST['ID_Empleado']),
                    'Fecha':          request.POST['Fecha'],
                    'Periodo':        request.POST['Periodo'],
                    'Resultado':      request.POST['Resultado'],
                    'Observaciones':  request.POST.get('Observaciones') or None,
                    'Evaluador':      request.POST.get('Evaluador') or None,
                }
                if eval_id:
                    Evaluacion.objects.filter(pk=eval_id).update(**datos)
                    msg = 'Evaluación actualizada correctamente.'
                else:
                    Evaluacion.objects.create(**datos)
                    msg = 'Evaluación registrada correctamente.'
                return JsonResponse({'ok': True, 'msg': msg})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        if accion == 'eliminar_evaluacion':
            try:
                Evaluacion.objects.filter(pk=int(request.POST['ID_Evaluacion'])).delete()
                return JsonResponse({'ok': True, 'msg': 'Evaluación eliminada.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

    # GET
    if rol == 'admin':
        evaluaciones = Evaluacion.objects.select_related(
            'ID_Empleado__ID_Persona', 'ID_Empleado__ID_Cargo'
        ).order_by('-Fecha')
        empleados = Empleado.objects.select_related('ID_Persona', 'ID_Cargo').filter(
            Estado_Empleado='Activo'
        )
    else:
        evaluaciones = Evaluacion.objects.filter(ID_Empleado=emp).order_by('-Fecha')
        empleados    = []

    ctx = {
        'evaluaciones': evaluaciones,
        'empleados':    empleados,
        'nombre':       request.session.get('nombre'),
        'rol':          rol,
        'emp':          emp,
    }
    return render(request, 'asistencia/evaluaciones.html', ctx)


# ══════════════════════════════════════════════════════════════════
#  CAPACITACIONES (R20)
# ══════════════════════════════════════════════════════════════════

@login_required_view
def capacitaciones_view(request):
    from .models import Capacitacion, EmpleadoCapacitacion
    rol = request.session.get('rol')
    emp = get_empleado_sesion(request)

    if request.method == 'POST' and rol == 'admin':
        accion = request.POST.get('accion')

        if accion == 'guardar_capacitacion':
            try:
                cap_id   = int(request.POST.get('ID_Capacitacion', 0) or 0)
                material = request.FILES.get('Material')
                datos = {
                    'Titulo':       request.POST['Titulo'],
                    'Descripcion':  request.POST.get('Descripcion') or None,
                    'Tipo':         request.POST.get('Tipo', 'Presencial'),
                    'Fecha_Evento': request.POST.get('Fecha_Evento') or None,
                    'Lugar':        request.POST.get('Lugar') or None,
                }
                if cap_id:
                    cap = Capacitacion.objects.get(pk=cap_id)
                    for k, v in datos.items():
                        setattr(cap, k, v)
                    if material:
                        cap.Material = material
                    cap.save()
                    msg = 'Capacitación actualizada correctamente.'
                else:
                    cap = Capacitacion(**datos)
                    if material:
                        cap.Material = material
                    cap.save()
                    # Asignar a todos los empleados activos automáticamente
                    empleados_activos = Empleado.objects.filter(Estado_Empleado='Activo')
                    EmpleadoCapacitacion.objects.bulk_create([
                        EmpleadoCapacitacion(ID_Empleado=e, ID_Capacitacion=cap, Estado='Pendiente')
                        for e in empleados_activos
                    ])
                    msg = f'Capacitación publicada y asignada a {empleados_activos.count()} empleados.'
                return JsonResponse({'ok': True, 'msg': msg})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        if accion == 'eliminar_capacitacion':
            try:
                Capacitacion.objects.filter(pk=int(request.POST['ID_Capacitacion'])).delete()
                return JsonResponse({'ok': True, 'msg': 'Capacitación eliminada.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

        if accion == 'actualizar_estado_cap':
            try:
                EmpleadoCapacitacion.objects.filter(
                    ID_Empleado_id=int(request.POST['ID_Empleado']),
                    ID_Capacitacion_id=int(request.POST['ID_Capacitacion']),
                ).update(
                    Estado=request.POST['Estado'],
                    Fecha_Completado=request.POST.get('Fecha_Completado') or None,
                )
                return JsonResponse({'ok': True, 'msg': 'Estado actualizado.'})
            except Exception as e:
                return JsonResponse({'ok': False, 'msg': f'Error: {e}'})

    # GET
    if rol == 'admin':
        capacitaciones = Capacitacion.objects.order_by('-Fecha_Publicacion')
        asignaciones   = EmpleadoCapacitacion.objects.select_related(
            'ID_Empleado__ID_Persona', 'ID_Capacitacion'
        ).order_by('ID_Capacitacion', 'ID_Empleado__ID_Persona__Apellidos')
        empleados = Empleado.objects.select_related('ID_Persona').filter(Estado_Empleado='Activo')
    else:
        capacitaciones = Capacitacion.objects.order_by('-Fecha_Publicacion')
        asignaciones   = EmpleadoCapacitacion.objects.filter(ID_Empleado=emp).select_related('ID_Capacitacion')
        empleados      = []

    ctx = {
        'capacitaciones': capacitaciones,
        'asignaciones':   asignaciones,
        'empleados':      empleados,
        'nombre':         request.session.get('nombre'),
        'rol':            rol,
        'emp':            emp,
    }
    return render(request, 'asistencia/capacitaciones.html', ctx)