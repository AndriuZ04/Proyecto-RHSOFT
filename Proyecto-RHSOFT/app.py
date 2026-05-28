from flask import Flask, request, render_template, redirect, url_for, flash
# Importamos la variable 'conexion' desde la carpeta 'database'
from database.conexion import conexion

app = Flask(__name__)
# Necesario para usar 'flash' (mensajes de error en la interfaz)
app.secret_key = 'mi_clave_secreta_super_segura' 

# 1. RUTA PARA MOSTRAR EL FORMULARIO DE LOGIN
@app.route('/')
def login_vista():
    return render_template('login.html')

# 2. RUTA PARA VALIDAR LAS CREDENCIALES (POST)
@app.route('/validar-login', methods=['POST'])
def validar_login():
    usuario = request.form['usuario']
    password = request.form['password']

    cursor = conexion.cursor()

    # Tu consulta SQL coincide perfectamente con la tabla `usuarios` de tu archivo SQL
    sql = """
    SELECT usuario, rol FROM usuarios 
    WHERE usuario = %s AND password = %s
    """
    valores = (usuario, password)
    
    cursor.execute(sql, valores)
    # fetchone() devuelve una tupla con los datos si existe, o None si no existe
    resultado = cursor.fetchone() 
    
    cursor.close() # Siempre es buena práctica cerrar el cursor

    if resultado:
        # resultado[0] es el usuario, resultado[1] es el rol ('Administrador' o 'Empleado')
        rol = resultado[1]
        
        if rol == 'Administrador':
            return redirect(url_for('menu_administrador'))
        elif rol == 'Empleado':
            return redirect(url_for('menu_empleado'))
        
        return "LOGIN CORRECTO"
    else:
        # Si falla, puedes enviar un mensaje de error y recargar el login
        return "USUARIO O CONTRASEÑA INCORRECTOS"

# 3. RUTAS DE EJEMPLO PARA REDIRECCIONAR SEGÚN EL ROL
@app.route('/menu-administrador')
def menu_administrador():
    return render_template('menu_administrador.html')

@app.route('/menu-empleado')
def menu_empleado():
    return render_template('menu_empleado.html')


# EJECUTAR SERVIDOR FLASK
if __name__ == '__main__':
    app.run(debug=True)