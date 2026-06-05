from flask import render_template
from flask import redirect
from flask import session
from flask import flash

from config.db import mysql


# ==========================
# VER ASISTENCIA
# ==========================

def ver_asistencia():

    registros = []

    return render_template(
        "empleado/asistencia.html",
        registros=registros
    )


# ==========================
# REGISTRAR ENTRADA
# ==========================

def marcar_entrada():

    id_usuario = session["id_usuario"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id_empleado
        FROM empleados
        WHERE id_usuario=%s
    """, (id_usuario,))

    empleado = cursor.fetchone()

    if empleado:

        id_empleado = empleado[0]

        cursor.execute("""
            SELECT id_registro
            FROM registros
            WHERE id_empleado=%s
            AND fecha=CURDATE()
        """, (id_empleado,))

        existe = cursor.fetchone()

        if not existe:

            cursor.execute("""
                INSERT INTO registros
                (
                    id_empleado,
                    fecha,
                    hora_entrada
                )
                VALUES
                (
                    %s,
                    CURDATE(),
                    CURTIME()
                )
            """, (id_empleado,))

            mysql.connection.commit()

            flash(
                "Entrada registrada correctamente",
                "success"
            )

        else:

            flash(
                "Ya registraste tu entrada hoy",
                "warning"
            )

    return redirect("/asistencia")


# ==========================
# REGISTRAR SALIDA
# ==========================

def marcar_salida():

    id_usuario = session["id_usuario"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id_empleado
        FROM empleados
        WHERE id_usuario=%s
    """, (id_usuario,))

    empleado = cursor.fetchone()

    if empleado:

        id_empleado = empleado[0]

        cursor.execute("""
            SELECT id_registro, hora_salida
            FROM registros
            WHERE id_empleado=%s
            AND fecha=CURDATE()
        """, (id_empleado,))

        registro = cursor.fetchone()

        if registro:

            if registro[1] is None:

                cursor.execute("""
                    UPDATE registros
                    SET hora_salida=CURTIME()
                    WHERE id_registro=%s
                """, (registro[0],))

                mysql.connection.commit()

                flash(
                    "Salida registrada correctamente",
                    "success"
                )

            else:

                flash(
                    "Ya registraste tu salida hoy",
                    "warning"
                )

# ==========================
# REGISTROS ADMIN
# ==========================

def listar_registros():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            CONCAT(p.nombres,' ',p.apellidos) AS empleado,
            r.fecha,
            r.hora_entrada,
            r.hora_salida
        FROM registros r

        INNER JOIN empleados e
            ON r.id_empleado = e.id_empleado

        INNER JOIN personas p
            ON e.id_persona = p.id_persona

        ORDER BY r.fecha DESC
    """)

    registros = cursor.fetchall()

    return render_template(
        "admin/registros.html",
        registros=registros
    )

# ==========================
# PERFIL EMPLEADO
# ==========================

def perfil_empleado():

    id_usuario = session["id_usuario"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            CONCAT(p.nombres,' ',p.apellidos),
            u.correo,
            c.nombre,
            d.nombre,
            p.documento,
            e.fecha_ingreso,
            e.estado

        FROM empleados e

        INNER JOIN personas p
            ON e.id_persona = p.id_persona

        INNER JOIN usuarios u
            ON e.id_usuario = u.id_usuario

        INNER JOIN cargos c
            ON e.id_cargo = c.id_cargo

        INNER JOIN departamentos d
            ON e.id_departamento = d.id_departamento

        WHERE e.id_usuario=%s
    """, (id_usuario,))

    empleado = cursor.fetchone()

    return render_template(
        "empleado/perfil.html",
        empleado=empleado
    )

# ==========================
# DASHBOARD EMPLEADO
# ==========================

def dashboard_empleado():

    id_usuario = session["id_usuario"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            CONCAT(p.nombres,' ',p.apellidos),
            c.nombre,
            d.nombre,
            e.estado

        FROM empleados e

        INNER JOIN personas p
            ON e.id_persona = p.id_persona

        INNER JOIN cargos c
            ON e.id_cargo = c.id_cargo

        INNER JOIN departamentos d
            ON e.id_departamento = d.id_departamento

        WHERE e.id_usuario=%s
    """, (id_usuario,))

    empleado = cursor.fetchone()

    return render_template(
        "empleado/dashboard.html",
        empleado=empleado
    )

    return redirect("/asistencia")