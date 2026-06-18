from flask import render_template
from config.db import mysql
from datetime import date


def dashboard_admin():

    cursor = mysql.connection.cursor()

    # Empleados activos

    cursor.execute("""
        SELECT COUNT(*)
        FROM empleados
        WHERE estado='ACTIVO'
    """)

    empleados_activos = cursor.fetchone()[0]

    # Empleados inactivos

    cursor.execute("""
        SELECT COUNT(*)
        FROM empleados
        WHERE estado='INACTIVO'
    """)

    empleados_inactivos = cursor.fetchone()[0]

    # Departamentos

    cursor.execute("""
        SELECT COUNT(*)
        FROM departamentos
    """)

    total_departamentos = cursor.fetchone()[0]

    # Cargos

    cursor.execute("""
        SELECT COUNT(*)
        FROM cargos
    """)

    total_cargos = cursor.fetchone()[0]

    # Contratos

    cursor.execute("""
        SELECT COUNT(*)
        FROM contratos
    """)

    total_contratos = cursor.fetchone()[0]

    # Vacaciones

    cursor.execute("""
        SELECT COUNT(*)
        FROM vacaciones
    """)

    total_vacaciones = cursor.fetchone()[0]

    # Permisos

    cursor.execute("""
        SELECT COUNT(*)
        FROM permisos
    """)

    total_permisos = cursor.fetchone()[0]

    # Registros de hoy

    cursor.execute("""
        SELECT COUNT(*)
        FROM registros
        WHERE fecha = CURDATE()
    """)

    registros_hoy = cursor.fetchone()[0]

    return render_template(
    "admin/dashboard.html",
    empleados_activos=empleados_activos,
    empleados_inactivos=empleados_inactivos,
    total_departamentos=total_departamentos,
    total_cargos=total_cargos,
    total_contratos=total_contratos,
    total_vacaciones=total_vacaciones,
    total_permisos=total_permisos,
    registros_hoy=registros_hoy,
    fecha_actual=date.today()
)