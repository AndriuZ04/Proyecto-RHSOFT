# RHSOFT

Sistema web de gestión de recursos humanos desarrollado con Python/Django y MySQL. Proyecto de formación del SENA (tecnólogo en desarrollo de software), con cumplimiento de la normativa laboral colombiana.

## Funcionalidades

- Inicio de sesión con correo y contraseña (contraseñas con hash)
- Recuperación de contraseña por correo
- Registro y control de asistencia
- Gestión de empleados, cargos y capacitaciones
- Evaluaciones de desempeño
- Postulaciones y selección de candidatos
- Panel de administración y perfil de usuario
- [Nómina / prestaciones, si aplica]

## Stack

Python 3.10+ · Django · MySQL/MariaDB · HTML/CSS · Arquitectura MVT con ORM de Django

## Estructura

```
├── manage.py
├── requirements.txt
├── seed_data.py          # datos de demostración
├── .env.example          # variables de entorno requeridas
├── rhsoft/               # configuración (settings, urls, wsgi)
└── asistencia/           # app principal
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── fixtures/
    ├── migrations/
    └── templates/asistencia/
```

## Instalación

1. Clonar y crear entorno virtual:
```bash
git clone https://github.com/AndriuZ04/Proyecto-RHSOFT.git
cd Proyecto-RHSOFT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Crear la base de datos en MySQL:
```sql
CREATE DATABASE gestion_empleados CHARACTER SET utf8mb4;
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
```
Completar en `.env`: `DB_PASSWORD`, `SECRET_KEY`, `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` (este último solo para el envío de correos).

4. Migrar y cargar datos de prueba:
```bash
python manage.py migrate
python seed_data.py
```

5. Ejecutar:
```bash
python manage.py runserver
```
Abrir http://127.0.0.1:8000/

## Credenciales de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Empleado | camilo.rodriguez@rhsoft.com | Empleado2026 |
| [Admin] | [correo del admin] | [contraseña] |

Son datos ficticios solo para pruebas.

## Autor

Andriu David Zambrano Velasco — [LinkedIn / zandriu04@gmail.com]
