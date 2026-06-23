from flask import render_template, request, redirect
from config.db import mysql

# ==========================
# LISTAR PERMISOS
# ==========================
def listar_permisos():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT
            p.id_permiso,
            CONCAT(pe.nombres,' ',pe.apellidos),
            p.motivo,
            p.fecha_inicio,
            p.fecha_fin,
            p.estado
        FROM permisos p
        INNER JOIN empleados e
            ON p.id_empleado = e.id_empleado
        INNER JOIN personas pe
            ON e.id_persona = pe.id_persona
        ORDER BY p.id_permiso
    """)
    permisos = cursor.fetchall()
    cursor.close()  # Cierre seguro del cursor

    return render_template(
        "admin/permisos.html",
        permisos=permisos
    )

# ==========================
# NUEVO PERMISO
# ==========================
def nuevo_permiso():
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
        "admin/nuevo_permiso.html",
        empleados=empleados
    )

# ==========================
# GUARDAR PERMISO
# ==========================
def guardar_permiso():
    id_empleado = request.form["id_empleado"]
    motivo = request.form["motivo"].strip()
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"].strip()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO permisos
        (id_empleado, motivo, fecha_inicio, fecha_fin, estado)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_empleado, motivo, fecha_inicio, fecha_fin, estado))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/permisos")

# ==========================
# EDITAR PERMISO
# ==========================
def editar_permiso(id_permiso):
    cursor = mysql.connection.cursor()
    
    # Traemos la información específica del permiso
    cursor.execute("""
        SELECT id_permiso, id_empleado, motivo, fecha_inicio, fecha_fin, estado
        FROM permisos
        WHERE id_permiso=%s
    """, (id_permiso,))
    permiso = cursor.fetchone()

    # Traemos la lista de empleados ordenada para el combobox
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
        "admin/editar_permiso.html",
        permiso=permiso,
        empleados=empleados
    )

# ==========================
# ACTUALIZAR PERMISO
# ==========================
def actualizar_permiso(id_permiso):
    id_empleado = request.form["id_empleado"]
    motivo = request.form["motivo"].strip()
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    estado = request.form["estado"].strip()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE permisos
        SET
            id_empleado=%s,
            motivo=%s,
            fecha_inicio=%s,
            fecha_fin=%s,
            estado=%s
        WHERE id_permiso=%s
    """, (id_empleado, motivo, fecha_inicio, fecha_fin, estado, id_permiso))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/permisos")

# ==========================
# ELIMINAR PERMISO
# ==========================
def eliminar_permiso(id_permiso):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        DELETE FROM permisos
        WHERE id_permiso=%s
    """, (id_permiso,))
    
    mysql.connection.commit()
    cursor.close()

    return redirect("/permisos")