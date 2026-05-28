from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# CONEXION MYSQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rrhh_empresa"
)

# LOGIN
@app.route('/')
def login():
    return render_template('login.html')

# MENU EMPLEADO
@app.route('/menu-empleado')
def menu_empleado():
    return render_template('menu_empleado.html')

# PERFIL
@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

# MENU ADMIN
@app.route('/menu-admin')
def menu_admin():
    return render_template('menu_admin.html')

# PROCESO SELECCION
@app.route('/seleccion')
def seleccion():
    return render_template('seleccion.html')

# VALIDAR LOGIN
@app.route('/validar-login', methods=['POST'])
def validar_login():

    usuario = request.form['usuario']
    password = request.form['password']

    cursor = conexion.cursor()

    sql = """
    SELECT * FROM usuarios
    WHERE usuario = %s
    AND password = %s
    """

    valores = (usuario, password)

    cursor.execute(sql, valores)

    resultado = cursor.fetchone()

    if resultado:
        return "Login correcto"

    else:
        return "Usuario incorrecto"

# EJECUTAR SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)