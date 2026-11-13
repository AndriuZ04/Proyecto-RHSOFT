import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhsoft.settings')
django.setup()

from datetime import date, time, timedelta
from django.contrib.auth.hashers import make_password
from asistencia.models import (
    Departamento, Cargo, CargoDia, Persona, Empleado, Contrato,
    Registro, Evaluacion, Postulacion,
)

print('Creando departamentos y cargos...')
dep_rh   = Departamento.objects.create(Nombre_Departamento='Recursos Humanos')
dep_tec  = Departamento.objects.create(Nombre_Departamento='Tecnología')
dep_ven  = Departamento.objects.create(Nombre_Departamento='Ventas')
dep_cont = Departamento.objects.create(Nombre_Departamento='Contabilidad')

cargo_dev = Cargo.objects.create(
    ID_Departamento=dep_tec, Nombre_Cargo='Desarrollador Backend',
    Descripcion_Funciones='Desarrollo y mantenimiento de aplicaciones internas.',
    Requisitos='Conocimientos en Python, Django y bases de datos relacionales.',
    Salario_Base=2800000, Hora_Inicio_Jornada=time(8,0), Hora_Fin_Jornada=time(17,0),
)
cargo_vend = Cargo.objects.create(
    ID_Departamento=dep_ven, Nombre_Cargo='Asesor Comercial',
    Descripcion_Funciones='Atención y asesoría a clientes, cierre de ventas.',
    Requisitos='Experiencia en ventas y atención al cliente.',
    Salario_Base=1900000, Hora_Inicio_Jornada=time(9,0), Hora_Fin_Jornada=time(18,0),
)
cargo_cont = Cargo.objects.create(
    ID_Departamento=dep_cont, Nombre_Cargo='Auxiliar Contable',
    Descripcion_Funciones='Registro y control de movimientos contables.',
    Requisitos='Técnico o tecnólogo en contabilidad.',
    Salario_Base=1750905, Hora_Inicio_Jornada=time(8,0), Hora_Fin_Jornada=time(16,0),
)

dias_lv = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
for cargo in [cargo_dev, cargo_vend, cargo_cont]:
    for dia in dias_lv:
        CargoDia.objects.create(ID_Cargo=cargo, Dia_Semana=dia)

print('Creando personas y empleados...')
PASSWORD_DEMO = make_password('Empleado2026')

personas_data = [
    dict(doc='1019432876', nom='Laura',     ape='Martínez Gómez',  email='laura.martinez@rhsoft.com',   tel='3112345678', fnac=date(1990,4,12),  cargo=cargo_dev,  rol='empleado'),
    dict(doc='1098765432', nom='Camilo',    ape='Rodríguez Pérez', email='camilo.rodriguez@rhsoft.com', tel='3123456789', fnac=date(1995,7,3),   cargo=cargo_dev,  rol='empleado'),
    dict(doc='1045678912', nom='Valentina', ape='López Castro',    email='valentina.lopez@rhsoft.com',  tel='3134567890', fnac=date(1998,11,20), cargo=cargo_vend, rol='empleado'),
    dict(doc='1087654321', nom='Andrés',    ape='Suárez Ramírez',  email='andres.suarez@rhsoft.com',    tel='3145678901', fnac=date(1992,2,15),  cargo=cargo_cont, rol='empleado'),
    dict(doc='1076543219', nom='Daniela',   ape='Torres Vargas',   email='daniela.torres@rhsoft.com',   tel='3156789012', fnac=date(1996,9,8),   cargo=cargo_vend, rol='empleado'),
]

empleados = {}
for p in personas_data:
    persona = Persona.objects.create(
        Numero_Documento=p['doc'], Nombres=p['nom'], Apellidos=p['ape'],
        Email=p['email'], Password=PASSWORD_DEMO, Telefono=p['tel'], Fecha_Nacimiento=p['fnac'],
    )
    emp = Empleado.objects.create(
        ID_Persona=persona, ID_Cargo=p['cargo'], Rol=p['rol'],
        Fecha_Ingreso=date(2025,1,15), Estado_Empleado='Activo',
    )
    Contrato.objects.create(
        ID_Empleado=emp, ID_Cargo=p['cargo'], Tipo_Contrato='Indefinido',
        Salario_Pactado=p['cargo'].Salario_Base, Fecha_Inicio=date(2025,1,15),
        Estado_Contrato='Vigente',
    )
    empleados[p['email']] = emp

print('Creando registros de asistencia de ejemplo...')
hoy = date.today()
for i in range(5):
    dia = hoy - timedelta(days=i)
    for emp in empleados.values():
        Registro.objects.create(
            ID_Empleado=emp, Fecha=dia, Hora_Entrada=time(8,2),
            Hora_Salida=time(17,5), Tipo='Normal',
        )

print('Creando evaluaciones de ejemplo...')
Evaluacion.objects.create(
    ID_Empleado=empleados['camilo.rodriguez@rhsoft.com'], Fecha=hoy, Periodo='Trimestral',
    Resultado='Excelente', Observaciones='Buen desempeño en entregas técnicas.',
    Evaluador='Laura Martínez',
)
Evaluacion.objects.create(
    ID_Empleado=empleados['valentina.lopez@rhsoft.com'], Fecha=hoy, Periodo='Mensual',
    Resultado='Bueno', Observaciones='Cumple metas de ventas mensuales.',
    Evaluador='Laura Martínez',
)

print('Creando postulaciones de ejemplo...')
postulante1 = Persona.objects.create(
    Numero_Documento='1067891234', Nombres='Sebastián', Apellidos='Mejía Ortiz',
    Email='sebastian.mejia@gmail.com', Telefono='3167891234', Fecha_Nacimiento=date(1999,5,30),
)
Postulacion.objects.create(
    ID_Persona=postulante1, Cargo_Aspirado=cargo_dev, Hoja_Vida='hojas_de_vida/demo_cv.pdf',
    Estado='Pendiente',
)
postulante2 = Persona.objects.create(
    Numero_Documento='1023456789', Nombres='Mariana', Apellidos='Restrepo Cárdenas',
    Email='mariana.restrepo@gmail.com', Telefono='3178912345', Fecha_Nacimiento=date(2001,8,14),
)
Postulacion.objects.create(
    ID_Persona=postulante2, Cargo_Aspirado=cargo_vend, Hoja_Vida='hojas_de_vida/demo_cv2.pdf',
    Estado='Pendiente',
)

print('¡Listo! Datos de prueba agregados sin afectar tus cuentas existentes.')
print('Credenciales de prueba para empleados:')
print('  camilo.rodriguez@rhsoft.com / Empleado2026')
print('  (mismo password para los demás empleados de prueba)')
