# RHSOFT — Migración PHP → Django

Sistema de gestión de asistencia y empleados migrado a Python/Django.

## Estructura del proyecto

```
rhsoft/
├── manage.py
├── requirements.txt
├── rhsoft/                  ← Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── asistencia/              ← Tu módulo (equivale a los .php originales)
    ├── models.py            ← Tablas de la BD como clases Python
    ├── views.py             ← Lógica (index.php + registro.php + admin.php)
    ├── urls.py              ← Rutas
    └── templates/
        └── asistencia/
            ├── base.html
            ├── login.html   ← index.php
            ├── registro.html← registro.php
            └── admin.html   ← admin.php
```

## Instalación paso a paso

### 1. Requisitos previos
- Python 3.10 o superior
- XAMPP corriendo (MySQL/MariaDB)
- La base de datos `gestion_empleados` ya importada

### 2. Instalar dependencias

```bash
# Abre una terminal en la carpeta rhsoft/
pip install -r requirements.txt
```

> Si hay error con mysqlclient en Windows, instala primero:
> `pip install mysqlclient` desde https://www.lfd.uci.edu/~gohlke/pythonlibs/

### 3. Configurar la base de datos

Abre `rhsoft/settings.py` y ajusta si es necesario:
```python
DATABASES = {
    'default': {
        'NAME':     'gestion_empleados',
        'USER':     'root',
        'PASSWORD': '',   # ← tu contraseña si tienes
        'HOST':     'localhost',
        'PORT':     '3306',
    }
}
```

### 4. Preparar sesiones de Django

```bash
python manage.py migrate --run-syncdb
```

Esto crea la tabla de sesiones en tu BD existente sin tocar las demás tablas.

### 5. Correr el servidor

```bash
python manage.py runserver
```

Abre en el navegador: **http://127.0.0.1:8000/**

### 6. Iniciar sesión

- **Admin:** PIN `999999`
- **Empleado de prueba:** PIN `123456`

---

## Equivalencias PHP → Python

| PHP              | Django/Python           |
|------------------|------------------------|
| `config.php`     | `settings.py`          |
| `index.php`      | `views.login_view`     |
| `registro.php`   | `views.registro_view`  |
| `admin.php`      | `views.admin_view`     |
| `PDO + SQL`      | Django ORM (models.py) |
| `$_SESSION`      | `request.session`      |
| `$_POST`         | `request.POST`         |
| `header(Location)`| `redirect()`          |
| `json_encode`    | `JsonResponse()`       |
| `<?= $var ?>`    | `{{ variable }}`       |

---

## Agregar módulos de compañeros

En `rhsoft/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'asistencia',
    'nomina',      # ← módulo de compañero 1
    'sst_externo', # ← módulo de compañero 2
]
```

En `rhsoft/urls.py`:
```python
urlpatterns = [
    path('',        include('asistencia.urls')),
    path('nomina/', include('nomina.urls')),
]
```

Cada módulo es una carpeta con su propio `models.py`, `views.py`, `urls.py` y `templates/`.
