from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Conexión MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="proyecto"
)

# ─────────────────────────────
# LOGIN
# ─────────────────────────────
@app.route("/")
def login():
    return render_template("login.html")

# ─────────────────────────────
# VALIDAR LOGIN
# ─────────────────────────────
@app.route("/validar", methods=["POST"])
def validar():
    cursor = conexion.cursor(dictionary=True)

    usuario    = request.form["usuario"]
    contraseña = request.form["contraseña"]

    sql    = "SELECT * FROM usuarios WHERE Nombre_Usuario=%s AND Contrasena=%s"
    cursor.execute(sql, (usuario, contraseña))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado:
        session["id_empleado"] = resultado["ID_Empleado"]  # ✅ guardar en sesión
        return redirect("/main")
    else:
        return "Datos incorrectos"

# ─────────────────────────────
# MAIN
# ─────────────────────────────
@app.route("/main")
def main():
    id_empleado = session.get("id_empleado")
    if not id_empleado:
        return redirect("/")  # si no hay sesión, vuelve al login

    cursor = conexion.cursor(dictionary=True)

    # Datos del empleado: une personas + empleados + cargos + departamentos
    sql_empleado = """
        SELECT
            p.Numero_Documento  AS Documento,
            p.Nombres,
            p.Apellidos,
            p.Email             AS Correo,
            p.Telefono,
            c.Nombre_Cargo,
            d.Nombre_Departamento AS Departamento,
            e.Estado_Empleado   AS Estado,
            e.ID_Empleado
        FROM empleados e
        JOIN personas     p ON e.ID_Persona     = p.ID_Persona
        JOIN cargos       c ON e.ID_Cargo        = c.ID_Cargo
        JOIN departamentos d ON c.ID_Departamento = d.ID_Departamento
        WHERE e.ID_Empleado = %s
    """
    cursor.execute(sql_empleado, (id_empleado,))
    empleado = cursor.fetchone()

    # Último registro de asistencia del empleado
    sql_registro = """
        SELECT Hora_Entrada, Hora_Salida
        FROM registros
        WHERE ID_Empleado = %s
        ORDER BY Fecha DESC, Hora_Entrada DESC
        LIMIT 1
    """
    cursor.execute(sql_registro, (id_empleado,))
    ultimo_registro = cursor.fetchone()

    # Total de días trabajados este mes
    sql_dias = """
        SELECT COUNT(*) AS total
        FROM registros
        WHERE ID_Empleado = %s
          AND MONTH(Fecha) = MONTH(CURDATE())
          AND YEAR(Fecha)  = YEAR(CURDATE())
    """
    cursor.execute(sql_dias, (id_empleado,))
    resultado_dias = cursor.fetchone()
    total_dias = resultado_dias["total"] if resultado_dias else 0

    # Contrato vigente del empleado
    sql_contrato = """
        SELECT Tipo_Contrato
        FROM contratos
        WHERE ID_Empleado = %s
        ORDER BY Fecha_Inicio DESC
        LIMIT 1
    """
    cursor.execute(sql_contrato, (id_empleado,))
    contrato = cursor.fetchone()

    cursor.close()

    return render_template(
        "main.HTML",
        empleado=empleado,
        ultimo_registro=ultimo_registro,
        total_dias=total_dias,
        contrato=contrato
    )

if __name__ == "__main__":
    app.run(debug=True)