from flask import render_template, request, redirect
from config.db import mysql

def listar_cargos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cargos")
    cargos = cursor.fetchall()
    return render_template('admin/cargos.html', cargos=cargos)

def nuevo_cargo():
    return render_template('admin/nuevo_cargo.html')

def guardar_cargo():
    nombre = request.form['nombre']
    salario = request.form['salario']
    descripcion = request.form['descripcion']
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO cargos (nombre, salario_referencia, descripcion) VALUES (%s, %s, %s)",
        (nombre, salario, descripcion)
    )
    mysql.connection.commit()
    return redirect('/cargos')

def editar_cargo(id_cargo):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cargos WHERE id_cargo = %s", (id_cargo,))
    cargo = cursor.fetchone()
    return render_template('admin/editar_cargo.html', cargo=cargo)

def actualizar_cargo(id_cargo):
    nombre = request.form['nombre']
    salario = request.form['salario']
    descripcion = request.form['descripcion']
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE cargos
        SET nombre = %s, salario_referencia = %s, descripcion = %s
        WHERE id_cargo = %s
    """, (nombre, salario, descripcion, id_cargo))
    mysql.connection.commit()
    return redirect('/cargos')

def eliminar_cargo(id_cargo):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cargos WHERE id_cargo = %s", (id_cargo,))
    mysql.connection.commit()
    return redirect('/cargos')