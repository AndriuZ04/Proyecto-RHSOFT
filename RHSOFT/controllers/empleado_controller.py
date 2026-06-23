from flask import render_template, request, redirect
from config.db import mysql

# ==========================
# LISTAR EMPLEADOS
# ==========================
def listar_empleados():
    cursor = mysql.connection.cursor()
    sql = """
    SELECT
        e.id_empleado,
        CONCAT(p.nombres,' ',p.apellidos) AS nombre_completo,
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
    LEFT JOIN contratos con
        ON e.id_empleado = con.id_empleado
    ORDER BY e.id_empleado
    """
    cursor.execute(sql)
    empleados = cursor.fetchall()
    cursor.close()

    return render_template(
        "admin/empleados.html",
        empleados=empleados
    )

# ==========================
# NUEVO EMPLEADO
# ==========================
def nuevo_empleado():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_cargo, nombre
        FROM cargos
        ORDER BY nombre
    """)
    cargos = cursor.fetchall()

    cursor.execute("""
        SELECT id_departamento, nombre
        FROM departamentos
        ORDER BY nombre
    """)
    departamentos = cursor.fetchall()
    cursor.close()

    return render_template(
        "admin/nuevo_empleado.html",
        cargos=cargos,
        departamentos=departamentos
    )

# ==========================
# GUARDAR EMPLEADO
# ==========================
def guardar_empleado():
    nombres = request.form["nombres"].strip()
    apellidos = request.form["apellidos"].strip()
    documento = request.form["documento"].strip()
    telefono = request.form["telefono"].strip()
    correo = request.form["correo"].strip()
    direccion = request.form["direccion"].strip()
    fecha_nacimiento = request.form["fecha_nacimiento"]
    genero = request.form["genero"]
    id_cargo = request.form["id_cargo"]
    id_departamento = request.form["id_departamento"]
    password = request.form["password"].strip()
    fecha_ingreso = request.form["fecha_ingreso"]

    cursor = mysql.connection.cursor()

    # PERSONAS
    cursor.execute("""
        INSERT INTO personas
        (nombres, apellidos, documento, telefono, correo, direccion, fecha_nacimiento, genero)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (nombres, apellidos, documento, telefono, correo, direccion, fecha_nacimiento, genero))
    mysql.connection.commit()
    id_persona = cursor.lastrowid

    # USUARIO
    cursor.execute("""
        INSERT INTO usuarios
        (correo, password, rol, estado)
        VALUES (%s,%s,'EMPLEADO','ACTIVO')
    """, (correo, password))
    mysql.connection.commit()
    id_usuario = cursor.lastrowid

    # EMPLEADO
    cursor.execute("""
        INSERT INTO empleados
        (id_persona, id_departamento, id_cargo, id_usuario, fecha_ingreso, estado)
        VALUES (%s,%s,%s,%s,%s,'ACTIVO')
    """, (id_persona, id_departamento, id_cargo, id_usuario, fecha_ingreso))
    mysql.connection.commit()
    cursor.close()

    return redirect("/empleados")

# ==========================
# EDITAR EMPLEADO
# ==========================
def editar_empleado(id_empleado):
    cursor = mysql.connection.cursor()
    sql = """
        SELECT
            e.id_empleado,
            p.nombres,
            p.apellidos,
            p.telefono,
            p.direccion
        FROM empleados e
        INNER JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.id_empleado = %s
    """
    cursor.execute(sql, (id_empleado,))
    empleado = cursor.fetchone()
    cursor.close()

    return render_template(
        "admin/editar_empleado.html",
        empleado=empleado
    )

# ==========================
# ACTUALIZAR EMPLEADO
# ==========================
def actualizar_empleado(id_empleado):
    nombres = request.form["nombres"].strip()
    apellidos = request.form["apellidos"].strip()
    telefono = request.form["telefono"].strip()
    direccion = request.form["direccion"].strip()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_persona
        FROM empleados
        WHERE id_empleado=%s
    """, (id_empleado,))
    
    resultado = cursor.fetchone()
    if resultado:
        id_persona = resultado[0]
        cursor.execute("""
            UPDATE personas
            SET nombres=%s, apellidos=%s, telefono=%s, direccion=%s
            WHERE id_persona=%s
        """, (nombres, apellidos, telefono, direccion, id_persona))
        mysql.connection.commit()
    
    cursor.close()
    return redirect("/empleados")

# ==========================
# ELIMINAR / DESACTIVAR EMPLEADO
# ==========================
def eliminar_empleado(id_empleado):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_usuario
        FROM empleados
        WHERE id_empleado = %s
    """, (id_empleado,))
    resultado = cursor.fetchone()

    if resultado:
        id_usuario = resultado[0]
        
        cursor.execute("""
            UPDATE empleados
            SET estado='INACTIVO'
            WHERE id_empleado=%s
        """, (id_empleado,))

        cursor.execute("""
            UPDATE usuarios
            SET estado='INACTIVO'
            WHERE id_usuario=%s
        """, (id_usuario,))
        mysql.connection.commit()

    cursor.close()
    return redirect("/empleados")

# ==========================
# ACTIVAR EMPLEADO novamente
# ==========================
def activar_empleado(id_empleado):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_usuario
        FROM empleados
        WHERE id_empleado = %s
    """, (id_empleado,))
    resultado = cursor.fetchone()

    if resultado:
        id_usuario = resultado[0]
        
        cursor.execute("""
            UPDATE empleados
            SET estado='ACTIVO'
            WHERE id_empleado=%s
        """, (id_empleado,))

        cursor.execute("""
            UPDATE usuarios
            SET estado='ACTIVO'
            WHERE id_usuario=%s
        """, (id_usuario,))
        mysql.connection.commit()

    cursor.close()
    return redirect("/empleados")