from flask import render_template

from config.db import mysql

from flask import request
from flask import redirect

def listar_departamentos():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id_departamento,
            nombre,
            descripcion
        FROM departamentos
        ORDER BY id_departamento
    """)

    departamentos = cursor.fetchall()

    return render_template(
        "admin/departamentos.html",
        departamentos=departamentos
    )

def nuevo_departamento():

    return render_template(
        "admin/nuevo_departamento.html"
    )

def guardar_departamento():

    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO departamentos
        (
            nombre,
            descripcion
        )
        VALUES
        (
            %s,
            %s
        )
    """, (
        nombre,
        descripcion
    ))

    mysql.connection.commit()

def editar_departamento(id_departamento):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id_departamento,
            nombre,
            descripcion
        FROM departamentos
        WHERE id_departamento=%s
    """, (id_departamento,))

    departamento = cursor.fetchone()

    return render_template(
        "admin/editar_departamento.html",
        departamento=departamento
    )

def actualizar_departamento(id_departamento):

    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE departamentos
        SET
            nombre=%s,
            descripcion=%s
        WHERE id_departamento=%s
    """, (
        nombre,
        descripcion,
        id_departamento
    ))

    mysql.connection.commit()

def eliminar_departamento(id_departamento):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM departamentos
        WHERE id_departamento=%s
    """, (id_departamento,))

    mysql.connection.commit()

    return redirect("/departamentos")
