from flask import render_template, request, redirect, flash
from config.db import mysql

def listar_cargos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cargos")
    cargos = cursor.fetchall()
    cursor.close()  # Cerramos el cursor de manera segura
    return render_template('admin/cargos.html', cargos=cargos)

def nuevo_cargo():
    return render_template('admin/nuevo_cargo.html')

def guardar_cargo():
    # .strip() elimina espacios vacíos innecesarios al inicio y al final
    nombre = request.form['nombre'].strip()
    salario = request.form['salario'].strip()
    descripcion = request.form['descripcion'].strip()
    
    # Validación básica para evitar inserciones vacías
    if not nombre or not salario:
        # Aquí puedes usar flash() si tienes configuradas alertas en tu HTML
        return redirect('/cargos')

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO cargos (nombre, salario_referencia, descripcion) VALUES (%s, %s, %s)",
        (nombre, salario, descripcion)
    )
    mysql.connection.commit()
    cursor.close()
    return redirect('/cargos')

def editar_cargo(id_cargo):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cargos WHERE id_cargo = %s", (id_cargo,))
    cargo = cursor.fetchone()
    cursor.close()
    return render_template('admin/editar_cargo.html', cargo=cargo)

def actualizar_cargo(id_cargo):
    nombre = request.form['nombre'].strip()
    salario = request.form['salario'].strip()
    descripcion = request.form['descripcion'].strip()
    
    if not nombre or not salario:
        return redirect('/cargos')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE cargos
        SET nombre = %s, salario_referencia = %s, descripcion = %s
        WHERE id_cargo = %s
    """, (nombre, salario, descripcion, id_cargo))
    mysql.connection.commit()
    cursor.close()
    return redirect('/cargos')

def eliminar_cargo(id_cargo):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cargos WHERE id_cargo = %s", (id_cargo,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/cargos')