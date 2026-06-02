from flask import render_template
from flask import request
from flask import redirect
from flask import session

from config.db import mysql


def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE correo=%s
            AND password=%s
            AND estado='ACTIVO'
        """, (correo, password))

        usuario = cursor.fetchone()

        if usuario:

            session["id_usuario"] = usuario[0]
            session["correo"] = usuario[1]
            session["rol"] = usuario[3]

            if usuario[3] == "ADMIN":
                return redirect("/admin")

            return redirect("/empleado")

        return render_template(
            "login.html",
            error="Correo o contraseña incorrectos"
        )

    return render_template("login.html")


def logout():

    session.clear()

    return redirect("/")