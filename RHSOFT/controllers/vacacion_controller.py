from flask import render_template
from config.db import mysql
from flask import request
from flask import redirect

def listar_vacaciones():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            v.id_vacacion,
            CONCAT(p.nombres,' ',p.apellidos),
            v.fecha_inicio,
            v.fecha_fin,
            v.dias,
            v.estado

        FROM vacaciones v

        INNER JOIN empleados e
            ON v.id_empleado = e.id_empleado

        INNER JOIN personas p
            ON e.id_persona = p.id_persona

        ORDER BY v.id_vacacion
    """)

    vacaciones = cursor.fetchall()

    return render_template(
        "admin/vacaciones.html",
        vacaciones=vacaciones
    )

def nueva_vacacion():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            e.id_empleado,
            CONCAT(p.nombres,' ',p.apellidos)
        FROM empleados e
        INNER JOIN personas p
            ON e.id_persona = p.id_persona
        ORDER BY p.nombres
    """)

    empleados = cursor.fetchall()

    return render_template(
        "admin/nueva_vacacion.html",
        empleados=empleados
    )

def guardar_vacacion():

    id_empleado = request.form["id_empleado"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    dias = request.form["dias"]
    estado = request.form["estado"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO vacaciones
        (
            id_empleado,
            fecha_inicio,
            fecha_fin,
            dias,
            estado
        )
        VALUES
        (%s,%s,%s,%s,%s)
    """, (
        id_empleado,
        fecha_inicio,
        fecha_fin,
        dias,
        estado
    ))

    mysql.connection.commit()

    return redirect("/vacaciones")

def editar_vacacion(id_vacacion):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT *
        FROM vacaciones
        WHERE id_vacacion=%s
    """, (id_vacacion,))

    vacacion = cursor.fetchone()

    cursor.execute("""
        SELECT
            e.id_empleado,
            CONCAT(p.nombres,' ',p.apellidos)
        FROM empleados e
        INNER JOIN personas p
            ON e.id_persona = p.id_persona
    """)

    empleados = cursor.fetchall()

    return render_template(
        "admin/editar_vacacion.html",
        vacacion=vacacion,
        empleados=empleados
    )

def actualizar_vacacion(id_vacacion):

    id_empleado = request.form["id_empleado"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    dias = request.form["dias"]
    estado = request.form["estado"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE vacaciones
        SET
            id_empleado=%s,
            fecha_inicio=%s,
            fecha_fin=%s,
            dias=%s,
            estado=%s
        WHERE id_vacacion=%s
    """, (
        id_empleado,
        fecha_inicio,
        fecha_fin,
        dias,
        estado,
        id_vacacion
    ))

    mysql.connection.commit()

    return redirect("/vacaciones")

def eliminar_vacacion(id_vacacion):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM vacaciones
        WHERE id_vacacion=%s
    """, (id_vacacion,))

    mysql.connection.commit()

    return redirect("/vacaciones")