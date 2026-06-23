from flask import render_template, request, redirect
from config.db import mysql

# ==========================
# LISTAR CONTRATOS
# ==========================
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
    cursor.close()  # Cerramos el cursor de manera segura

    return render_template(
        "admin/contratos.html",
        contratos=contratos
    )

# ==========================
# NUEVO CONTRATO
# ==========================
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
    cursor.close()

    return render_template(
        "admin/nuevo_contrato.html",
        empleados=empleados
    )

# ==========================
# GUARDAR CONTRATO
# ==========================
def guardar_contrato():
    id_empleado = request.form["id_empleado"]
    tipo_contrato = request.form["tipo_contrato"].strip()
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"].strip()

    # Si la fecha de fin viene vacía (ej. contrato indefinido), se guarda como NULL
    if not fecha_fin:
        fecha_fin = None

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO contratos
        (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, estado)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, estado))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/contratos")

# ==========================
# EDITAR CONTRATO
# ==========================
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
    cursor.close()

    return render_template(
        "admin/editar_contrato.html",
        contrato=contrato,
        empleados=empleados
    )

# ==========================
# ACTUALIZAR CONTRATO
# ==========================
def actualizar_contrato(id_contrato):
    id_empleado = request.form["id_empleado"]
    tipo_contrato = request.form["tipo_contrato"].strip()
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"].strip()

    if not fecha_fin:
        fecha_fin = None

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
    """, (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, estado, id_contrato))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/contratos")

# ==========================
# ELIMINAR CONTRATO
# ==========================
def eliminar_contrato(id_contrato):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        DELETE FROM contratos
        WHERE id_contrato=%s
    """, (id_contrato,))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/contratos")