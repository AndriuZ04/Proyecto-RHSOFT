from flask import render_template, redirect, session, flash, request
from config.db import mysql
import os
from werkzeug.utils import secure_filename

# ==========================
# VER ASISTENCIA
# ==========================
def ver_asistencia():
    id_usuario = session["id_usuario"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id_empleado
        FROM empleados
        WHERE id_usuario = %s
    """, (id_usuario,))
    empleado = cursor.fetchone()

    registros = []

    if empleado:
        id_empleado = empleado[0]
        cursor.execute("""
            SELECT
                fecha,
                hora_entrada,
                hora_salida
            FROM registros
            WHERE id_empleado = %s
            ORDER BY fecha DESC
        """, (id_empleado,))
        registros = cursor.fetchall()

    cursor.close()  # Cierre unificado y seguro

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
        SELECT
            e.id_empleado,
            p.nombres
        FROM empleados e
        INNER JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.id_usuario=%s
    """, (id_usuario,))
    empleado = cursor.fetchone()

    if empleado:
        id_empleado = empleado[0]
        nombre_empleado = empleado[1]

        cursor.execute("""
            SELECT id_registro
            FROM registros
            WHERE id_empleado=%s
            AND fecha=CURDATE()
        """, (id_empleado,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("""
                INSERT INTO registros (id_empleado, fecha, hora_entrada)
                VALUES (%s, CURDATE(), CURTIME())
            """, (id_empleado,))
            mysql.connection.commit()

            flash(
                f"👋 Hola {nombre_empleado}, tu entrada fue registrada correctamente. ¡Te deseamos una excelente jornada laboral!",
                "success"
            )
        else:
            flash(
                f"⚠️ {nombre_empleado}, ya registraste tu entrada hoy.",
                "warning"
            )

    cursor.close()
    return redirect("/asistencia")

# ==========================
# REGISTRAR SALIDA
# ==========================
def marcar_salida():
    id_usuario = session["id_usuario"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            e.id_empleado,
            p.nombres
        FROM empleados e
        INNER JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.id_usuario=%s
    """, (id_usuario,))
    empleado = cursor.fetchone()

    if not empleado:
        cursor.close()
        flash("Empleado no encontrado", "warning")
        return redirect('/asistencia')

    id_empleado = empleado[0]
    nombre_empleado = empleado[1]

    cursor.execute("""
        SELECT id_registro, hora_salida
        FROM registros
        WHERE id_empleado=%s
        AND fecha=CURDATE()
    """, (id_empleado,))
    registro = cursor.fetchone()

    if not registro:
        cursor.close()
        flash(
            f"⚠️ {nombre_empleado}, primero debes registrar tu entrada antes de registrar la salida.",
            "warning"
        )
        return redirect('/asistencia')

    if registro[1] is None:
        cursor.execute("""
            UPDATE registros
            SET hora_salida=CURTIME()
            WHERE id_registro=%s
        """, (registro[0],))
        mysql.connection.commit()

        flash(
            f"🎉 Hasta luego {nombre_empleado}. Tu salida fue registrada correctamente. Gracias por tu trabajo de hoy.",
            "success"
        )
    else:
        flash(
            f"⚠️ {nombre_empleado}, ya registraste tu salida hoy.",
            "warning"
        )

    cursor.close()
    return redirect('/asistencia')

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
    cursor.close()

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
            ON e.id_departmento = d.id_departamento
        WHERE e.id_usuario=%s
    """, (id_usuario,))
    empleado = cursor.fetchone()
    cursor.close()

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
    cursor.close()

    return render_template(
        "empleado/dashboard.html",
        empleado=empleado
    )

# ==========================
# SUBIR FOTO PERFIL
# ==========================
def subir_foto():
    foto = request.files["foto"]

    if foto:
        nombre_archivo = secure_filename(foto.filename)
        ruta = os.path.join("static", "uploads", "fotos", nombre_archivo)
        foto.save(ruta)

        id_usuario = session["id_usuario"]
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT id_persona
            FROM empleados
            WHERE id_usuario=%s
        """, (id_usuario,))
        persona = cursor.fetchone()

        if persona:
            cursor.execute("""
                UPDATE personas
                SET foto=%s
                WHERE id_persona=%s
            """, (nombre_archivo, persona[0]))
            mysql.connection.commit()

            # ACTUALIZA LA FOTO EN LA SESIÓN
            session["foto_empleado"] = nombre_archivo
        
        cursor.close()

    return redirect("/perfil")