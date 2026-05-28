# Documentación del Proyecto RHSOFT
## Sistema de Gestión de Asistencia y Empleados
### Migrado de PHP a Python/Django por Andriu David Zambrano Velasco — SENA 2026

---

## Estructura general del proyecto

```
rhsoft.py/                          ← Carpeta raíz del proyecto
├── manage.py                       ← Punto de entrada de Django (equivale a index.php en PHP)
├── requirements.txt                ← Lista de librerías necesarias (django, mysqlclient)
├── README.md                       ← Instrucciones de instalación
├── DOCUMENTACION.md                ← Este archivo
│
├── rhsoft/                         ← Configuración del proyecto Django
│   ├── settings.py                 ← Configuración general (BD, apps instaladas, etc.)
│   ├── urls.py                     ← Rutas principales del proyecto
│   ├── wsgi.py                     ← Punto de entrada para servidores de producción
│   └── __init__.py                 ← Archivo vacío que marca la carpeta como módulo Python
│
└── asistencia/                     ← Módulo principal (equivale a los .php originales)
    ├── models.py                   ← Tablas de la BD representadas como clases Python
    ├── views.py                    ← Lógica del sistema (login, registro, admin)
    ├── urls.py                     ← Rutas del módulo asistencia
    ├── __init__.py                 ← Archivo vacío que marca la carpeta como módulo Python
    │
    ├── fixtures/
    │   └── initial_data.json       ← Datos de ejemplo para cargar con loaddata
    │
    ├── migrations/                 ← Historial de cambios de la base de datos
    │   ├── __init__.py
    │   └── 0001_initial.py         ← Primera migración: crea todas las tablas
    │
    └── templates/
        └── asistencia/             ← Archivos HTML del sistema
            ├── base.html           ← Template base con estilos globales
            ├── login.html          ← Pantalla de ingreso con PIN
            ├── registro.html       ← Pantalla de marcación de asistencia
            └── admin.html          ← Panel de administración
```

---

## Archivos generados automáticamente (no editar)

| Archivo/Carpeta | Qué es |
|---|---|
| `__pycache__/` | Python compila los `.py` a bytecode para que corran más rápido. Se regenera sola. |
| `*.cpython-314.pyc` | El bytecode compilado. No se edita, se regenera automáticamente. |
| `migrations/0001_initial.py` | Generado por `makemigrations`. Describe cómo crear las tablas en la BD. |

---

## Archivo: `rhsoft/settings.py`
### Configuración central del proyecto

```python
SECRET_KEY        # Clave secreta para seguridad. Cambiar en producción.
DEBUG = True      # Muestra errores detallados. Cambiar a False en producción.
ALLOWED_HOSTS     # Dominios permitidos. En desarrollo: localhost y 127.0.0.1.

INSTALLED_APPS    # Lista de módulos activos. Aquí se agregan los módulos de compañeros.
                  # Ejemplo: 'nomina', 'sst_externo'

DATABASES         # Configuración de conexión a MySQL 8:
                  #   NAME     → nombre de la BD (gestion_empleados)
                  #   USER     → usuario (root)
                  #   PASSWORD → contraseña (root)
                  #   HOST     → servidor (localhost)
                  #   PORT     → puerto (3306)

SESSION_ENGINE    # Guarda las sesiones en la BD (equivale a $_SESSION en PHP)
TIME_ZONE         # Zona horaria Colombia: 'America/Bogota'
USE_TZ = False    # False para que las horas no se conviertan a UTC automáticamente
```

---

## Archivo: `rhsoft/urls.py`
### Rutas principales del proyecto

```python
path('', include('asistencia.urls'))
# Delega todas las rutas al módulo asistencia.
# Para agregar módulos de compañeros:
# path('nomina/', include('nomina.urls'))
```

---

## Archivo: `asistencia/urls.py`
### Rutas del módulo de asistencia

| URL | Vista | Nombre | Equivalente PHP |
|---|---|---|---|
| `/` | `login_view` | `login` | `index.php` |
| `/registro/` | `registro_view` | `registro` | `registro.php` |
| `/admin-panel/` | `admin_view` | `admin_panel` | `admin.php` |

---

## Archivo: `asistencia/models.py`
### Tablas de la base de datos como clases Python

Cada clase = una tabla en MySQL. Los campos son los equivalentes a las columnas.

### `Persona`
Guarda los datos personales de cualquier persona del sistema.
```
ID_Persona       → Clave primaria, se genera automáticamente
Numero_Documento → Cédula o documento. Único en la BD (no puede repetirse)
Nombres          → Nombres de la persona
Apellidos        → Apellidos de la persona
Email            → Correo electrónico (opcional)
Telefono         → Teléfono (opcional)
Fecha_Nacimiento → Fecha de nacimiento (opcional)
```
> `db_table = 'personas'` → le dice a Django que use la tabla `personas` en MySQL

### `Departamento`
Lista de departamentos de la empresa.
```
ID_Departamento     → Clave primaria
Nombre_Departamento → Nombre del departamento (ej: "Producción")
```

### `Cargo`
Cargos disponibles, cada uno pertenece a un departamento.
```
ID_Cargo              → Clave primaria
ID_Departamento       → ForeignKey a Departamento (relación muchos a uno)
Nombre_Cargo          → Nombre del cargo (ej: "Operario")
Descripcion_Funciones → Descripción de las funciones del cargo (opcional)
Salario_Base          → Salario base del cargo (opcional)
Hora_Inicio_Jornada   → Hora de inicio de la jornada laboral (opcional)
Hora_Fin_Jornada      → Hora de fin de la jornada laboral (opcional)
```
> `ForeignKey` con `on_delete=PROTECT` → no deja borrar un departamento si tiene cargos

### `CargoDia`
Días laborales de cada cargo (relación R17 del diagrama).
```
ID_Cargo   → ForeignKey a Cargo
Dia_Semana → Nombre del día (ej: "Lunes", "Martes")
```
> `unique_together` → no permite repetir el mismo día para el mismo cargo

### `Empleado`
Vincula una Persona con un Cargo y agrega datos laborales.
```
ID_Empleado     → Clave primaria
ID_Persona      → ForeignKey a Persona
ID_Cargo        → ForeignKey a Cargo
PIN             → Código de 6 dígitos para iniciar sesión. Único en la BD.
Rol             → 'admin' o 'empleado'
Fecha_Ingreso   → Fecha de ingreso a la empresa (opcional)
Fecha_Retiro    → Fecha de retiro. Null si sigue activo.
Estado_Empleado → 'Activo' o 'Inactivo'
```
> `nombre_completo` → propiedad que devuelve "Nombres Apellidos" sin consultar de nuevo

### `Contrato`
Contratos laborales de cada empleado (relación R13 del diagrama).
```
ID_Contrato     → Clave primaria
ID_Empleado     → ForeignKey a Empleado
ID_Cargo        → ForeignKey a Cargo (el cargo en el momento del contrato)
Tipo_Contrato   → 'Indefinido', 'Temporal' o 'Prácticas'
Salario_Pactado → Salario acordado en el contrato
Fecha_Inicio    → Inicio de vigencia del contrato
Fecha_Fin       → Fin del contrato. Null si es indefinido.
Estado_Contrato → 'Vigente', 'Terminado' o 'Suspendido'
```

### `Registro`
Marcaciones de entrada y salida de asistencia.
```
ID_Registro  → Clave primaria
ID_Empleado  → ForeignKey a Empleado
Fecha        → Fecha del registro
Hora_Entrada → Hora de entrada (obligatoria)
Hora_Salida  → Hora de salida (opcional, null si aún está en jornada)
Tipo         → 'Normal', 'Tarde', 'Salida anticipada', etc.
Observacion  → Nota adicional (opcional)
```

### `SstAccidente`
Registro de accidentes laborales (relación R14 del diagrama).
```
ID_Accidente     → Clave primaria
ID_Empleado      → ForeignKey a Empleado
Fecha_Accidente  → Fecha en que ocurrió el accidente
Tipo_Accidente   → 'Caída', 'Corte', 'Golpe', 'Quemadura', etc.
Descripcion      → Descripción detallada del accidente
Accion_Inmediata → Acción tomada en el momento (primeros auxilios, etc.)
Fecha_Reporte    → Fecha en que se reportó formalmente
```

---

## Archivo: `asistencia/views.py`
### Lógica del sistema

Equivale a los tres archivos PHP originales: `index.php`, `registro.php` y `admin.php`.

### Helpers (funciones de apoyo)

**`get_empleado_sesion(request)`**
Retorna el objeto Empleado de la sesión activa, o None si no hay sesión.
Equivale a leer `$_SESSION['empleado_id']` y hacer el SELECT en PHP.

**`login_required_view`**
Decorador que protege vistas: si no hay sesión, redirige al login.
Equivale al `if (!isset($_SESSION['empleado_id'])) header('Location: index.php')` de PHP.

**`admin_required_view`**
Decorador que protege vistas de admin: si el rol no es 'admin', redirige al login.

### `login_view` (equivale a `index.php`)
Maneja la pantalla de login con PIN.
- **GET** → muestra el formulario
- **GET con `?logout`** → destruye la sesión y redirige al login
- **POST con `pin`** → busca el empleado por PIN, crea la sesión y redirige según rol

### `registro_view` (equivale a `registro.php`)
Pantalla de marcación de asistencia del empleado.
- **GET** → muestra la pantalla con el reloj, historial y estadísticas del mes
- **POST AJAX con `accion=entrada`** → crea un registro de entrada (valida que no haya una activa)
- **POST AJAX con `accion=salida`** → completa el registro con la hora de salida

### `admin_view` (equivale a `admin.php`)
Panel de administración con gestión de empleados, contratos y SST.
- **GET** → renderiza el panel con la lista de empleados y KPIs
- **POST AJAX** → maneja múltiples acciones según el campo `accion`:

| Acción | Qué hace |
|---|---|
| `guardar_empleado` | Crea o actualiza un empleado y su persona asociada |
| `guardar_contrato` | Crea o actualiza un contrato (R13) |
| `guardar_sst` | Registra un accidente SST (R14) |
| `get_empleado` | Retorna datos de un empleado en JSON para el formulario de edición |
| `get_contratos` | Retorna los contratos de un empleado en JSON |
| `get_registros` | Retorna el historial de asistencia de un empleado en JSON |
| `get_sst` | Retorna los accidentes SST de un empleado en JSON |
| `cambiar_estado` | Cambia el estado (Activo/Inactivo) de un empleado |
| `eliminar_empleado` | Da de baja a un empleado (R12): lo marca Inactivo y cierra contratos |

---

## Templates HTML

Los templates usan **Django Template Language (DTL)**, muy similar a PHP con `<?= ?>`.

| Sintaxis PHP | Sintaxis Django |
|---|---|
| `<?= $variable ?>` | `{{ variable }}` |
| `<?php if($x): ?>` | `{% if x %}` |
| `<?php foreach($arr as $item): ?>` | `{% for item in arr %}` |
| `include 'header.php'` | `{% extends "base.html" %}` |
| `htmlspecialchars($x)` | `{{ x }}` (escapa automáticamente) |

### `base.html`
Template base con variables CSS globales (colores institucionales).
Todos los demás templates lo extienden con `{% extends "asistencia/base.html" %}`.

### `login.html`
Pantalla de acceso con teclado numérico virtual.
Usa JavaScript para capturar el PIN y enviarlo al servidor.
Incluye soporte para teclado físico (teclas 0-9 y Backspace).

### `registro.html`
Panel del empleado con:
- Reloj en tiempo real (JavaScript con `setInterval`)
- Botones de entrada/salida que llaman a la vista via AJAX (fetch API)
- Estadísticas del mes actual
- Historial de los últimos 30 registros
- Información del cargo, departamento y contrato vigente en el sidebar

### `admin.html`
Panel de administración con:
- KPIs: total empleados, activos, presentes hoy, accidentes del mes
- Tabla de empleados con filtro por nombre/documento y por estado
- Tabs: Empleados, Contratos (R13), SST (R14)
- Modales para crear/editar empleados, contratos y accidentes
- Todas las acciones usan AJAX (sin recargar la página)

---

## Equivalencias PHP → Django

| Concepto PHP | Equivalente Django/Python |
|---|---|
| `$_SESSION` | `request.session` |
| `$_POST` | `request.POST` |
| `$_GET` | `request.GET` |
| `header('Location: x')` | `redirect('nombre_url')` |
| `json_encode($data)` | `JsonResponse(data)` |
| `PDO + SQL manual` | Django ORM (models.py) |
| `SELECT * FROM ...` | `Modelo.objects.all()` |
| `WHERE campo = ?` | `.filter(campo=valor)` |
| `INSERT INTO ...` | `Modelo.objects.create(...)` |
| `UPDATE ... SET ...` | `.filter(...).update(...)` |

---

## Comandos útiles

```powershell
# Instalar dependencias
pip install -r requirements.txt

# Crear tablas en la BD
python manage.py migrate

# Cargar datos de ejemplo
python manage.py loaddata initial_data

# Correr el servidor de desarrollo
python manage.py runserver

# Cuando se modifica models.py, regenerar migraciones
python manage.py makemigrations asistencia
python manage.py migrate

# Consola interactiva de Python con Django cargado
python manage.py shell
```

---

## Cómo agregar el módulo de un compañero

1. Copia la carpeta del módulo dentro de `rhsoft.py/`
2. En `rhsoft/settings.py` agrega el módulo a `INSTALLED_APPS`:
   ```python
   'asistencia',
   'nomina',       # ← módulo del compañero
   ```
3. En `rhsoft/urls.py` agrega la ruta:
   ```python
   path('nomina/', include('nomina.urls')),
   ```
4. Corre `python manage.py migrate` para crear las tablas del nuevo módulo.
