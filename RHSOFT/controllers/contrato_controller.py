from flask import render_template
from config.db import mysql


from flask import request
from flask import redirect


def listar_contratos():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            c.id_contrato,
            CONCAT(p.nombres,' ',p.apellidos),
            c.tipo_contrato,
            c.fecha_inicio,
            c.fecha_fin,
            c.estado

        FROM contratos c

        INNER JOIN empleados e
            ON c.id_empleado = e.id_empleado

        INNER JOIN personas p
            ON e.id_persona = p.id_persona

        ORDER BY c.id_contrato
    """)

    contratos = cursor.fetchall()

    return render_template(
        "admin/contratos.html",
        contratos=contratos
    )

def nuevo_contrato():

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
        "admin/nuevo_contrato.html",
        empleados=empleados
    )



def guardar_contrato():

    id_empleado = request.form["id_empleado"]
    tipo_contrato = request.form["tipo_contrato"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO contratos
        (
            id_empleado,
            tipo_contrato,
            fecha_inicio,
            fecha_fin,
            estado
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        id_empleado,
        tipo_contrato,
        fecha_inicio,
        fecha_fin,
        estado
    ))

    mysql.connection.commit()

    return redirect("/contratos")

def editar_contrato(id_contrato):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id_contrato,
            id_empleado,
            tipo_contrato,
            fecha_inicio,
            fecha_fin,
            estado
        FROM contratos
        WHERE id_contrato=%s
    """, (id_contrato,))

    contrato = cursor.fetchone()

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
        "admin/editar_contrato.html",
        contrato=contrato,
        empleados=empleados
    )

def actualizar_contrato(id_contrato):

    id_empleado = request.form["id_empleado"]
    tipo_contrato = request.form["tipo_contrato"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE contratos
        SET
            id_empleado=%s,
            tipo_contrato=%s,
            fecha_inicio=%s,
            fecha_fin=%s,
            estado=%s
        WHERE id_contrato=%s
    """, (
        id_empleado,
        tipo_contrato,
        fecha_inicio,
        fecha_fin,
        estado,
        id_contrato
    ))

    mysql.connection.commit()

    return redirect("/contratos")

def eliminar_contrato(id_contrato):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM contratos
        WHERE id_contrato=%s
    """, (id_contrato,))

    mysql.connection.commit()

    return redirect("/contratos")