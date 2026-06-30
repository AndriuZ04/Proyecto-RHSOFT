from flask import render_template, request, redirect, flash
from config.db import mysql
from datetime import datetime, date, timedelta

# ==========================
# LISTAR CONTRATOS
# ==========================
def listar_contratos():
    cursor = mysql.connection.cursor()
    hoy_str = date.today().strftime("%Y-%m-%d")

    # Regla del Negocio Automática: Cambiar a 'TERMINADO' si la fecha de fin ya expiró
    try:
        cursor.execute("""
            UPDATE contratos 
            SET estado = 'TERMINADO' 
            WHERE fecha_fin IS NOT NULL AND fecha_fin < %s AND UPPER(TRIM(estado)) = 'ACTIVO'
        """, (hoy_str,))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()

    # --- CONSULTA DE ESTADÍSTICAS (KPIs) BLINDADA ---
    # Si el estado es NULL o vacío, lo sumamos a los inactivos por consistencia con tu tabla vieja
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN UPPER(TRIM(estado)) = 'ACTIVO' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN UPPER(TRIM(estado)) IN ('INACTIVO', 'FINALIZADO', 'TERMINADO') OR estado IS NULL OR TRIM(estado) = '' THEN 1 ELSE 0 END) AS inactivos
        FROM contratos
    """)
    stats_data = cursor.fetchone()
    
    stats = {
        'total': stats_data[0] if stats_data[0] else 0,
        'activos': stats_data[1] if stats_data[1] else 0,
        'inactivos': stats_data[2] if stats_data[2] else 0
    }

    # --- CONSULTA DE LA TABLA ---
    sql = """
        SELECT 
            c.id_contrato,
            CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
            c.tipo_contrato,
            c.fecha_inicio,
            c.fecha_fin,
            c.estado
        FROM contratos c
        INNER JOIN empleados e ON c.id_empleado = e.id_empleado
        INNER JOIN personas p ON e.id_persona = p.id_persona
        ORDER BY c.id_contrato DESC
    """
    cursor.execute(sql)
    contratos = cursor.fetchall()
    cursor.close()
    
    return render_template("admin/contratos.html", contratos=contratos, stats=stats)

# ==========================
# NUEVO CONTRATO (VISTA)
# ==========================
def nuevo_contrato():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT e.id_empleado, CONCAT(p.nombres, ' ', p.apellidos) AS nombre_completo
        FROM empleados e
        INNER JOIN personas p ON e.id_persona = p.id_persona
        WHERE e.estado = 'ACTIVO' 
          AND e.id_empleado NOT IN (
              SELECT id_empleado FROM contratos WHERE UPPER(TRIM(estado)) = 'ACTIVO'
          )
        ORDER BY p.nombres
    """)
    empleados = cursor.fetchall()
    cursor.close()
    return render_template("admin/nuevo_contrato.html", empleados=empleados)

# ==========================
# GUARDAR CONTRATO
# ==========================
def guardar_contrato():
    id_empleado = request.form.get("id_empleado")
    tipo_contrato = request.form.get("tipo_contrato")
    salario_str = request.form.get("salario", "").strip()
    fecha_inicio_str = request.form.get("fecha_inicio")
    fecha_fin_str = request.form.get("fecha_fin")

    if not (id_empleado and tipo_contrato and salario_str and fecha_inicio_str):
        flash("⚠️ Todos los campos marcados con asterisco (*) son obligatorios.", "warning")
        return redirect("/nuevo_contrato")

    try:
        salario = float(salario_str)
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        hoy = date.today()

        if salario < 1750905.0:
            flash("⚠️ El salario no puede ser menor al salario mínimo legal vigente de $1.750.905.", "danger")
            return redirect("/nuevo_contrato")

        if fecha_inicio < hoy:
            flash("⚠️ La fecha de inicio no puede ser una fecha anterior al día actual.", "danger")
            return redirect("/nuevo_contrato")
        
        if fecha_inicio > (hoy + timedelta(days=150)):
            flash("⚠️ La fecha de inicio no puede ser mayor a 5 meses en el futuro.", "danger")
            return redirect("/nuevo_contrato")

        fecha_fin_db = None
        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if fecha_fin <= fecha_inicio:
                flash("⚠️ La fecha de finalización debe ser posterior a la de inicio.", "danger")
                return redirect("/nuevo_contrato")
            
            if fecha_fin > (fecha_inicio + timedelta(days=365)):
                flash("⚠️ La fecha de finalización no puede superar el año de duración.", "danger")
                return redirect("/nuevo_contrato")
            fecha_fin_db = fecha_fin_str

    except ValueError:
        flash("⚠️ Los formatos de datos ingresados son inválidos.", "danger")
        return redirect("/nuevo_contrato")

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE contratos 
            SET estado = 'INACTIVO' 
            WHERE id_empleado = %s AND estado = 'ACTIVO'
        """, (id_empleado,))

        estado_inicial = 'ACTIVO'
        if fecha_inicio > hoy:
            estado_inicial = 'POR_INICIAR'

        cursor.execute("""
            INSERT INTO contratos (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_empleado, tipo_contrato, fecha_inicio_str, fecha_fin_db, estado_inicial))
        
        mysql.connection.commit()
        flash("✅ El contrato laboral ha sido asentado correctamente.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ Error técnico al guardar en la base de datos.", "danger")
    finally:
        cursor.close()

    return redirect("/contratos")

# ==========================
# EDITAR CONTRATO (VISTA)
# ==========================
def editar_contrato(id_contrato):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_contrato, id_empleado, tipo_contrato, fecha_inicio, fecha_fin, estado
        FROM contratos
        WHERE id_contrato = %s
    """, (id_contrato,))
    contrato = cursor.fetchone()

    cursor.execute("""
        SELECT e.id_empleado, CONCAT(p.nombres, ' ', p.apellidos) AS nombre_completo
        FROM empleados e
        INNER JOIN personas p ON e.id_persona = p.id_persona
        WHERE e.estado = 'ACTIVO'
        ORDER BY p.nombres
    """)
    empleados = cursor.fetchall()
    cursor.close()

    return render_template("admin/editar_contrato.html", contrato=contrato, empleados=empleados)

# ==========================
# ACTUALIZAR CONTRATO
# ==========================
def actualizar_contrato(id_contrato):
    id_empleado = request.form.get("id_empleado")
    tipo_contrato = request.form.get("tipo_contrato")
    fecha_inicio_str = request.form.get("fecha_inicio")
    fecha_fin_str = request.form.get("fecha_fin")
    estado = request.form.get("estado")

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if fecha_fin <= fecha_inicio:
                flash("⚠️ La fecha de finalización debe ser posterior a la de inicio.", "danger")
                return redirect(f"/editar_contrato/{id_contrato}")
    except ValueError:
        flash("⚠️ Los formatos de las fechas ingresadas no son válidos.", "danger")
        return redirect(f"/editar_contrato/{id_contrato}")

    fecha_fin_db = fecha_fin_str if fecha_fin_str else None

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE contratos
            SET id_empleado=%s, tipo_contrato=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s
            WHERE id_contrato=%s
        """, (id_empleado, tipo_contrato, fecha_inicio_str, fecha_fin_db, estado, id_contrato))
        mysql.connection.commit()
        flash("✅ Contrato modificado y validado correctamente.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ Error al intentar actualizar los datos.", "danger")
    finally:
        cursor.close()

    return redirect("/contratos")

# ==========================
# ELIMINAR / DESACTIVAR CONTRATO
# ==========================
def eliminar_contrato(id_contrato):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE contratos
            SET estado = 'INACTIVO'
            WHERE id_contrato = %s
        """, (id_contrato,))
        mysql.connection.commit()
        flash("🔒 Contrato finalizado y marcado como INACTIVO.", "info")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ No se pudo dar de baja el contrato.", "danger")
    finally:
        cursor.close()

    return redirect("/contratos")