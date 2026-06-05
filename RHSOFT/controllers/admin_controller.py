from flask import render_template
from config.db import mysql


def dashboard_admin():

    cursor = mysql.connection.cursor()

    # Total empleados

    cursor.execute("""
        SELECT COUNT(*)
        FROM empleados
    """)

    total_empleados = cursor.fetchone()[0]

    # Total departamentos

    cursor.execute("""
        SELECT COUNT(*)
        FROM departamentos
    """)

    total_departamentos = cursor.fetchone()[0]

    # Total cargos

    cursor.execute("""
        SELECT COUNT(*)
        FROM cargos
    """)

    total_cargos = cursor.fetchone()[0]

    # Registros del día

    cursor.execute("""
        SELECT COUNT(*)
        FROM registros
        WHERE fecha = CURDATE()
    """)

    registros_hoy = cursor.fetchone()[0]

    return render_template(
        "admin/dashboard.html",
        total_empleados=total_empleados,
        total_departamentos=total_departamentos,
        total_cargos=total_cargos,
        registros_hoy=registros_hoy
    )