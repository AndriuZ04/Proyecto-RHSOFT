import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",            # Usuario por defecto en XAMPP
    password="",            # Contraseña por defecto (vacía)
    database="rrhh_empresa", # El nombre exacto de tu base de datos
    port=3306               # ¡Cambiado a 3306!
)