from flask import render_template, request, redirect
from config.db import mysql

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
    cursor.close()  # Cerramos el cursor de manera segura
    
    return render_template(
        "admin/departamentos.html",
        departamentos=departamentos
    )

def nuevo_departamento():
    return render_template(
        "admin/nuevo_departamento.html"
    )

def guardar_departamento():
    nombre = request.form["nombre"].strip()
    descripcion = request.form["descripcion"].strip()

    if not nombre:
        return redirect("/departamentos")

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
    cursor.close()  # Cerramos el cursor
    
    return redirect("/departamentos")  # Agregado el retorno faltante

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
    cursor.close()  # Cerramos el cursor
    
    return render_template(
        "admin/editar_departamento.html",
        departamento=departamento
    )

def actualizar_departamento(id_departamento):
    nombre = request.form["nombre"].strip()
    descripcion = request.form["descripcion"].strip()

    if not nombre:
        return redirect("/departamentos")

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
    cursor.close()  # Cerramos el cursor
    
    return redirect("/departamentos")  # Agregado el retorno faltante

def eliminar_departamento(id_departamento):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        DELETE FROM departamentos
        WHERE id_departamento=%s
    """, (id_departamento,))
    mysql.connection.commit()
    cursor.close()  # Cerramos el cursor
    
    return redirect("/departamentos")