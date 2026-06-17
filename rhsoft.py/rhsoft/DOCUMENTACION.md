# RHSOFT — Documentación del Proyecto

Sistema de gestión de empleados y asistencia desarrollado en Python/Django con MySQL 8.0.

---

## Estructura del proyecto

```
rhsoft/
├── manage.py
├── requirements.txt
├── media/                        ← Archivos subidos (hojas de vida)
│   └── hojas_de_vida/
├── rhsoft/                       ← Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── asistencia/                   ← Módulo principal
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_postulacion.py
    ├── fixtures/
    │   └── initial_data.json
    └── templates/
        └── asistencia/
            ├── base.html
            ├── login.html
            ├── registro.html
            ├── admin.html
            ├── perfil.html
            ├── postulacion.html
            └── seleccion.html
```

---

## Módulos y responsables

| Módulo | Responsable | Descripción |
|---|---|---|
| Login + registro de asistencia | Andriu | Autenticación por PIN, marcado de entrada/salida |
| Gestión de empleados | Andriu | Panel admin: empleados, contratos, SST |
| Perfil del empleado | Jerson | Ver y editar datos personales |
| Proceso de selección | Jerson | Postulaciones y contratación |
| Menú empleado | Cristian | Cubierto por el módulo de asistencia de Andriu |

---

## Modelo de datos

### `personas`
Datos personales de cualquier individuo en el sistema (empleados y postulantes).

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Persona | INT (PK) | Identificador único |
| Numero_Documento | VARCHAR(50) | Cédula o pasaporte — único en el sistema |
| Nombres | VARCHAR(150) | Nombres completos |
| Apellidos | VARCHAR(150) | Apellidos |
| Email | VARCHAR(150) | Correo electrónico (opcional) |
| Telefono | VARCHAR(30) | Teléfono (opcional) |
| Fecha_Nacimiento | DATE | Fecha de nacimiento (opcional) |

### `departamentos`
Áreas de la empresa.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Departamento | INT (PK) | Identificador único |
| Nombre_Departamento | VARCHAR(150) | Nombre del área |

### `cargos`
Posiciones disponibles dentro de cada departamento.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Cargo | INT (PK) | Identificador único |
| ID_Departamento | FK → departamentos | Área a la que pertenece |
| Nombre_Cargo | VARCHAR(150) | Nombre del cargo |
| Descripcion_Funciones | VARCHAR(500) | Funciones del cargo |
| Salario_Base | DECIMAL(15,2) | Salario base del cargo |
| Hora_Inicio_Jornada | TIME | Hora de inicio de la jornada |
| Hora_Fin_Jornada | TIME | Hora de fin de la jornada |

### `cargo_dias`
Días laborales de cada cargo (ej: Lunes, Martes...).

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Cargo | FK → cargos | Cargo al que aplica |
| Dia_Semana | VARCHAR(20) | Nombre del día (ej: "Lunes") |

### `empleados`
Personas vinculadas laboralmente a la empresa.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Empleado | INT (PK) | Identificador único |
| ID_Persona | FK → personas | Datos personales |
| ID_Cargo | FK → cargos | Cargo actual |
| PIN | VARCHAR(6) | Código de acceso al sistema — único |
| Rol | ENUM | `admin` o `empleado` |
| Fecha_Ingreso | DATE | Fecha de vinculación |
| Fecha_Retiro | DATE | Fecha de retiro (nullable) |
| Estado_Empleado | ENUM | `Activo` o `Inactivo` |

### `contratos`
Historial contractual de cada empleado.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Contrato | INT (PK) | Identificador único |
| ID_Empleado | FK → empleados | Empleado vinculado |
| ID_Cargo | FK → cargos | Cargo del contrato |
| Tipo_Contrato | VARCHAR(100) | Indefinido, Temporal, Prácticas, etc. |
| Salario_Pactado | DECIMAL(15,2) | Salario acordado |
| Fecha_Inicio | DATE | Inicio de vigencia |
| Fecha_Fin | DATE | Fin de vigencia (nullable = indefinido) |
| Estado_Contrato | ENUM | `Vigente`, `Terminado` o `Suspendido` |

### `registros`
Marcaciones de asistencia diarias.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Registro | INT (PK) | Identificador único |
| ID_Empleado | FK → empleados | Empleado que marcó |
| Fecha | DATE | Fecha del registro |
| Hora_Entrada | TIME | Hora de entrada |
| Hora_Salida | TIME | Hora de salida (nullable) |
| Tipo | VARCHAR(80) | Tipo de jornada (Normal, etc.) |
| Observacion | VARCHAR(300) | Nota adicional (opcional) |

### `sst_accidentes`
Registro de accidentes laborales.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Accidente | INT (PK) | Identificador único |
| ID_Empleado | FK → empleados | Empleado involucrado |
| Fecha_Accidente | DATE | Fecha del accidente |
| Tipo_Accidente | VARCHAR(100) | Caída, Corte, Golpe, Otro... |
| Descripcion | VARCHAR(500) | Descripción del evento |
| Accion_Inmediata | VARCHAR(500) | Qué se hizo al momento |
| Fecha_Reporte | DATE | Fecha en que se reportó |

### `postulaciones`
Registro de candidatos en el proceso de selección.

| Campo | Tipo | Descripción |
|---|---|---|
| ID_Postulacion | INT (PK) | Identificador único |
| ID_Persona | FK → personas | Datos del postulante |
| Cargo_Aspirado | FK → cargos | Cargo al que aplica |
| Hoja_Vida | FILE | Archivo PDF subido |
| Estado | ENUM | `Pendiente`, `Aceptado`, `Entrevista`, `Rechazado`, `Contratado` |
| Fecha_Postulacion | DATE | Fecha en que se postuló (automática) |
| Observacion | VARCHAR(500) | Notas del admin sobre el candidato |

---

## URLs del sistema

| URL | Vista | Acceso | Descripción |
|---|---|---|---|
| `/` | `login_view` | Público | Pantalla de login con PIN |
| `/registro/` | `registro_view` | Empleado | Marcar entrada/salida del día |
| `/perfil/` | `perfil_view` | Empleado | Ver y editar datos personales |
| `/admin-panel/` | `admin_view` | Admin | Panel de gestión de empleados |
| `/seleccion/` | `seleccion_view` | Admin | Gestión del proceso de selección |
| `/postulacion/` | `postulacion_view` | Público | Formulario de postulación |

---

## Reglas de negocio implementadas

| Regla | Descripción | Dónde se valida |
|---|---|---|
| R10 | No se puede postular quien ya es empleado activo. No se puede postular dos veces al mismo cargo activamente. | `postulacion_view` |
| R13 | Un empleado activo siempre debe tener al menos un contrato vigente. | `admin_view` → `guardar_empleado`, `guardar_contrato` |
| R16 | El salario pactado no puede ser inferior al salario mínimo legal vigente ($ 1,750,905 para 2026). | `admin_view` → `guardar_cargo`, `guardar_empleado`, `seleccion_view` → `contratar` |
| R17 | Solo se puede registrar asistencia en los días laborales configurados para el cargo. | `registro_view` |

---

## Instalación y configuración

### Requisitos
- Python 3.10 o superior
- MySQL 8.0 standalone
- pip

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos
En `rhsoft/settings.py` ajusta si es necesario:
```python
DATABASES = {
    'default': {
        'NAME':     'gestion_empleados',
        'USER':     'root',
        'PASSWORD': 'root',
        'HOST':     'localhost',
        'PORT':     '3306',
    }
}
```

### 3. Crear la base de datos (MySQL)
```sql
CREATE DATABASE gestion_empleados CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Aplicar migraciones
```bash
python manage.py migrate
```

### 5. Cargar datos iniciales
```bash
python manage.py loaddata asistencia/fixtures/initial_data.json
```

### 6. Correr el servidor
```bash
python manage.py runserver
```

### 7. Acceder al sistema
- **URL:** http://127.0.0.1:8000/
- **Admin:** PIN `999999`
- **Empleado de prueba:** PIN `100001`
- **Formulario de postulación (público):** http://127.0.0.1:8000/postulacion/

---

## Archivos de medios (hojas de vida)

Los PDF subidos se guardan en `rhsoft/media/hojas_de_vida/`. Esta carpeta se crea automáticamente la primera vez que alguien sube un archivo. En producción, esta carpeta debe estar fuera del repositorio (agregar `media/` al `.gitignore`).

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.14 | Lenguaje base |
| Django | 6.0 | Framework web |
| MySQL | 8.0 | Base de datos |
| mysqlclient | — | Conector MySQL para Django |
| DM Sans / DM Serif Display | — | Tipografía (Google Fonts) |
