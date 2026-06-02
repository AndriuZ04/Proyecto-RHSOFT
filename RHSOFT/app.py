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
    eliminar_empleado
)
from controllers.cargo_controller import (
    listar_cargos,
    nuevo_cargo,
    guardar_cargo
)
from controllers.registro_controller import (
    ver_asistencia,
    marcar_entrada,
    marcar_salida
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

@app.route("/admin")
def admin_dashboard():
    return render_template(
        "admin/dashboard.html"
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
    eliminar_empleado
)
# ==========================
# REGISTROS
# ==========================

@app.route("/registros")
def registros():
    return render_template(
        "admin/registros.html"
    )

# ==========================
# EMPLEADO
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
@app.route("/empleado")
def dashboard_empleado():
    return render_template(
        "empleado/dashboard.html"
    )

@app.route("/perfil")
def perfil():
    return render_template(
        "empleado/perfil.html"
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