from flask import Flask
from flask import render_template

from config.db import mysql

from controllers.auth_controller import login
from controllers.auth_controller import logout

from controllers.empleado_controller import (
    listar_empleados,
    nuevo_empleado,
    guardar_empleado,
    editar_empleado,
    actualizar_empleado,
    eliminar_empleado,
    activar_empleado
)
from controllers.cargo_controller import (
    listar_cargos,
    nuevo_cargo,
    guardar_cargo,
    editar_cargo,
    actualizar_cargo,
    eliminar_cargo
)
from controllers.departamento_controller import (
    listar_departamentos,
    nuevo_departamento,
    guardar_departamento,
    editar_departamento,
    actualizar_departamento,
    eliminar_departamento
)
from controllers.registro_controller import (
    ver_asistencia,
    marcar_entrada,
    marcar_salida,
    listar_registros,
    perfil_empleado,
    dashboard_empleado,
    subir_foto
)
from controllers.admin_controller import (
    dashboard_admin
)
from controllers.contrato_controller import (
    listar_contratos,
    nuevo_contrato,
    guardar_contrato,
    editar_contrato,
    actualizar_contrato,
    eliminar_contrato
)
from controllers.vacacion_controller import (
    listar_vacaciones,
    nueva_vacacion,
    guardar_vacacion,
    editar_vacacion,
    actualizar_vacacion,
    eliminar_vacacion
)
from controllers.permiso_controller import (
    listar_permisos,
    nuevo_permiso,
    guardar_permiso,
    editar_permiso,
    actualizar_permiso,
    eliminar_permiso
)
app = Flask(__name__)

app.secret_key = "rhssoft"

# ==========================
# MYSQL
# ==========================

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "rhssoft"

mysql.init_app(app)

# ==========================
# LOGIN
# ==========================

app.add_url_rule(
    '/',
    'login',
    login,
    methods=['GET', 'POST']
)

# ==========================
# LOGOUT
# ==========================

app.add_url_rule(
    '/logout',
    'logout',
    logout
)

# ==========================
# ADMIN
# ==========================

app.add_url_rule(
    '/admin',
    'admin',
    dashboard_admin
)

# ==========================
# EMPLEADOS
# ==========================

app.add_url_rule(
    '/empleados',
    'empleados',
    listar_empleados
)

app.add_url_rule(
    '/nuevo_empleado',
    'nuevo_empleado',
    nuevo_empleado
)

app.add_url_rule(
    '/guardar_empleado',
    'guardar_empleado',
    guardar_empleado,
    methods=['POST']
)

app.add_url_rule(
    '/editar_empleado/<int:id_empleado>',
    'editar_empleado',
    editar_empleado
)

app.add_url_rule(
    '/actualizar_empleado/<int:id_empleado>',
    'actualizar_empleado',
    actualizar_empleado,
    methods=['POST']
)

app.add_url_rule(
    '/eliminar_empleado/<int:id_empleado>',
    'eliminar_empleado',
    eliminar_empleado,
    methods=['GET']
)
# ==========================
# REGISTROS
# ==========================
app.add_url_rule(
    '/registros',
    'registros',
    listar_registros
)

# ==========================
# CARGO
# ==========================

app.add_url_rule(
    '/cargos',
    'cargos',
    listar_cargos
)
app.add_url_rule(
    '/nuevo_cargo',
    'nuevo_cargo',
    nuevo_cargo
)
app.add_url_rule(
    '/guardar_cargo',
    'guardar_cargo',
    guardar_cargo,
    methods=['POST']
)
app.add_url_rule(
    '/editar_cargo/<int:id_cargo>',
    'editar_cargo',
    editar_cargo
)
app.add_url_rule(
    '/actualizar_cargo/<int:id_cargo>',
    'actualizar_cargo',
    actualizar_cargo,
    methods=['POST']
)
app.add_url_rule(
    '/eliminar_cargo/<int:id_cargo>',
    'eliminar_cargo',
    eliminar_cargo,
    methods=['POST']
)

# ==========================
# DEPARTAMENTO
# ==========================
app.add_url_rule(
    '/departamentos',
    'departamentos',
    listar_departamentos
)
app.add_url_rule(
    '/nuevo_departamento',
    'nuevo_departamento',
    nuevo_departamento
)

app.add_url_rule(
    '/guardar_departamento',
    'guardar_departamento',
    guardar_departamento,
    methods=['POST']
)
app.add_url_rule(
    '/editar_departamento/<int:id_departamento>',
    'editar_departamento',
    editar_departamento
)

app.add_url_rule(
    '/actualizar_departamento/<int:id_departamento>',
    'actualizar_departamento',
    actualizar_departamento,
    methods=['POST']
)
app.add_url_rule(
    '/eliminar_departamento/<int:id_departamento>',
    'eliminar_departamento',
    eliminar_departamento
)
# ==========================
# CONTRATO
# ==========================
app.add_url_rule(
    '/contratos',
    'contratos',
    listar_contratos
)
app.add_url_rule(
    '/nuevo_contrato',
    'nuevo_contrato',
    nuevo_contrato
)
app.add_url_rule(
    '/guardar_contrato',
    'guardar_contrato',
    guardar_contrato,
    methods=['POST']
)
app.add_url_rule(
    '/editar_contrato/<int:id_contrato>',
    'editar_contrato',
    editar_contrato
)
app.add_url_rule(
    '/actualizar_contrato/<int:id_contrato>',
    'actualizar_contrato',
    actualizar_contrato,
    methods=['POST']
)
app.add_url_rule(
    '/eliminar_contrato/<int:id_contrato>',
    'eliminar_contrato',
    eliminar_contrato
)
# ==========================
# EMPLEADO
# ==========================
app.add_url_rule(
    '/empleado',
    'empleado',
    dashboard_empleado
)

@app.route("/test_empleado")
def test_empleado():

    from flask import session

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id_empleado
        FROM empleados
        WHERE id_usuario=%s
    """, (session["id_usuario"],))

    empleado = cursor.fetchone()

    return str(empleado)

app.add_url_rule(
    '/activar_empleado/<int:id_empleado>',
    'activar_empleado',
    activar_empleado,
    methods=['GET']
)
# ==========================
# PERFIL
# ==========================
app.add_url_rule(
    '/perfil',
    'perfil',
    perfil_empleado
)

# ==========================
# SUBIR FOTO 
# ==========================
app.add_url_rule(
    '/subir_foto',
    'subir_foto',
    subir_foto,
    methods=['POST']
)
# ==========================
# ASISTENCIA
# ==========================

app.add_url_rule(
    '/asistencia',
    'asistencia',
    ver_asistencia
)

app.add_url_rule(
    '/marcar_entrada',
    'marcar_entrada',
    marcar_entrada
)

app.add_url_rule(
    '/marcar_salida',
    'marcar_salida',
    marcar_salida
)
# ==========================
# VACACIONES
# ==========================
app.add_url_rule(
    '/vacaciones',
    'vacaciones',
    listar_vacaciones
)
app.add_url_rule(
    '/nueva_vacacion',
    'nueva_vacacion',
    nueva_vacacion
)
app.add_url_rule(
    '/guardar_vacacion',
    'guardar_vacacion',
    guardar_vacacion,
    methods=['POST']
)
app.add_url_rule(
    '/editar_vacacion/<int:id_vacacion>',
    'editar_vacacion',
    editar_vacacion
)
app.add_url_rule(
    '/actualizar_vacacion/<int:id_vacacion>',
    'actualizar_vacacion',
    actualizar_vacacion,
    methods=['POST']
)
app.add_url_rule(
    '/eliminar_vacacion/<int:id_vacacion>',
    'eliminar_vacacion',
    eliminar_vacacion
)
# ==========================
# PERMISOS
# ==========================
app.add_url_rule(
    '/permisos',
    'permisos',
    listar_permisos
)
app.add_url_rule(
    '/nuevo_permiso',
    'nuevo_permiso',
    nuevo_permiso
)

app.add_url_rule(
    '/guardar_permiso',
    'guardar_permiso',
    guardar_permiso,
    methods=['POST']
)
app.add_url_rule(
    '/editar_permiso/<int:id_permiso>',
    'editar_permiso',
    editar_permiso
)
app.add_url_rule(
    '/actualizar_permiso/<int:id_permiso>',
    'actualizar_permiso',
    actualizar_permiso,
    methods=['POST']
)
app.add_url_rule(
    '/eliminar_permiso/<int:id_permiso>',
    'eliminar_permiso',
    eliminar_permiso
)
# ==========================
# TEST MYSQL
# ==========================

@app.route("/test_db")
def test_db():

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM usuarios"
    )

    total = cursor.fetchone()

    return f"Usuarios registrados: {total[0]}"

# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)