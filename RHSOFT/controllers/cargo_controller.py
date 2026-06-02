from flask import render_template
from flask import request
from flask import redirect

from config.db import mysql


# ==========================
# LISTAR CARGOS
# ==========================

def listar_cargos():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id_cargo,
            nombre,
            salario_referencia,
            descripcion
        FROM cargos
        ORDER BY id_cargo
    """)

    cargos = cursor.fetchall()

    return render_template(
        "admin/cargos.html",
        cargos=cargos
    )


# ==========================
# NUEVO CARGO
# ==========================

def nuevo_cargo():

    return render_template(
        "admin/nuevo_cargo.html"
    )


# ==========================
# GUARDAR CARGO
# ==========================

def guardar_cargo():

    nombre = request.form["nombre"]
    salario = request.form["salario"]
    descripcion = request.form["descripcion"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO cargos
        (
            nombre,
            salario_referencia,
            descripcion
        )
        VALUES
        (%s,%s,%s)
    """,
    (
        nombre,
        salario,
        descripcion
    ))

    mysql.connection.commit()

    return redirect("/cargos")