from flask import render_template, request, redirect, session
from config.db import mysql

# ==========================
# INICIAR SESIÓN
# ==========================
def login():
    if request.method == "POST":
        # Limpiamos espacios en blanco accidentales
        correo = request.form["correo"].strip()
        password = request.form["password"].strip()

        cursor = mysql.connection.cursor()

        # Buscamos el usuario activo
        cursor.execute("""
            SELECT id_usuario, correo, password, rol, estado
            FROM usuarios
            WHERE correo=%s
            AND password=%s
            AND estado='ACTIVO'
        """, (correo, password))

        usuario = cursor.fetchone()

        if usuario:
            # Guardamos datos base en la sesión
            session["id_usuario"] = usuario[0]
            session["correo"] = usuario[1]
            session["rol"] = usuario[3]

            # Si es empleado, traemos sus datos adicionales de la empresa
            if usuario[3] == "EMPLEADO":
                cursor.execute("""
                    SELECT
                        CONCAT(p.nombres,' ',p.apellidos),
                        c.nombre
                    FROM empleados e
                    INNER JOIN personas p
                        ON e.id_persona = p.id_persona
                    INNER JOIN cargos c
                        ON e.id_cargo = c.id_cargo
                    WHERE e.id_usuario=%s
                """, (usuario[0],))

                datos_empleado = cursor.fetchone()

                if datos_empleado:
                    session["nombre_empleado"] = datos_empleado[0]
                    session["cargo_empleado"] = datos_empleado[1]

            # Cerramos el cursor antes de cualquier redirección exitosa
            cursor.close()

            if usuario[3] == "ADMIN":
                return redirect("/admin")
                
            return redirect("/empleado")

        # Si el usuario no existe o está inactivo, cerramos el cursor y mandamos error
        cursor.close()
        return render_template(
            "login.html",
            error="Correo o contraseña incorrectos"
        )

    return render_template("login.html")

# ==========================
# CERRAR SESIÓN
# ==========================
def logout():
    session.clear()
    return redirect("/")    