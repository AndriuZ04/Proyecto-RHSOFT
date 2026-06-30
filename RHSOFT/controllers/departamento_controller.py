from flask import render_template, request, redirect, flash
from config.db import mysql

# ==========================
# LISTAR DEPARTAMENTOS
# ==========================
def listar_departamentos():
    cursor = mysql.connection.cursor()
    # Traemos los departamentos y contamos cuántos empleados activos pertenecen a cada uno
    cursor.execute("""
        SELECT 
            d.id_departamento,
            d.nombre,
            d.descripcion,
            (SELECT COUNT(*) FROM empleados e WHERE e.id_departamento = d.id_departamento AND e.estado = 'ACTIVO') AS total_empleados
        FROM departamentos d
        ORDER BY d.id_departamento DESC
    """)
    departamentos = cursor.fetchall()
    cursor.close()
    
    return render_template(
        "admin/departamentos.html",
        departamentos=departamentos
    )

# ==========================
# NUEVO DEPARTAMENTO (VISTA)
# ==========================
def nuevo_departamento():
    return render_template("admin/nuevo_departamento.html")

# ==========================
# GUARDAR DEPARTAMENTO
# ==========================
def guardar_departamento():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    if not nombre:
        flash("⚠️ El nombre del departamento es un campo obligatorio.", "warning")
        return redirect("/nuevo_departamento")

    cursor = mysql.connection.cursor()
    
    # VALIDACIÓN: Evitar nombres duplicados
    cursor.execute("SELECT id_departamento FROM departamentos WHERE UPPER(nombre) = UPPER(%s)", (nombre,))
    if cursor.fetchone():
        flash(f"⚠️ El área corporativa '{nombre}' ya se encuentra registrada en el sistema.", "danger")
        cursor.close()
        return redirect("/nuevo_departamento")

    try:
        cursor.execute("""
            INSERT INTO departamentos (nombre, descripcion)
            VALUES (%s, %s)
        """, (nombre, descripcion))
        mysql.connection.commit()
        flash(f"✅ El departamento '{nombre}' ha sido creado exitosamente.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ Error técnico al intentar registrar el departamento.", "danger")
    finally:
        cursor.close()
    
    return redirect("/departamentos")

# ==========================
# EDITAR DEPARTAMENTO (VISTA)
# ==========================
def editar_departamento(id_departamento):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_departamento, nombre, descripcion
        FROM departamentos
        WHERE id_departamento = %s
    """, (id_departamento,))
    departamento = cursor.fetchone()
    cursor.close()
    
    if not departamento:
        flash("⚠️ El departamento solicitado no existe.", "warning")
        return redirect("/departamentos")
        
    return render_template(
        "admin/editar_departamento.html",
        departamento=departamento
    )

# ==========================
# ACTUALIZAR DEPARTAMENTO
# ==========================
def actualizar_departamento(id_departamento):
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    if not nombre:
        flash("⚠️ El nombre modificado no puede estar vacío.", "warning")
        return redirect(f"/editar_departamento/{id_departamento}")

    cursor = mysql.connection.cursor()
    
    # VALIDACIÓN: Evitar duplicar nombre con OTRO departamento diferente al actual
    cursor.execute("""
        SELECT id_departamento FROM departamentos 
        WHERE UPPER(nombre) = UPPER(%s) AND id_departamento != %s
    """, (nombre, id_departamento))
    
    if cursor.fetchone():
        flash(f"⚠️ Ya existe otra área registrada con el nombre '{nombre}'.", "danger")
        cursor.close()
        return redirect(f"/editar_departamento/{id_departamento}")

    try:
        cursor.execute("""
            UPDATE departamentos
            SET nombre = %s, descripcion = %s
            WHERE id_departamento = %s
        """, (nombre, descripcion, id_departamento))
        mysql.connection.commit()
        flash("✅ Estructura del departamento actualizada correctamente.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ Error técnico al intentar modificar el área.", "danger")
    finally:
        cursor.close()
    
    return redirect("/departamentos")

# ==========================
# ELIMINAR DEPARTAMENTO (CON INTEGRIDAD)
# ==========================
def eliminar_departamento(id_departamento):
    cursor = mysql.connection.cursor()
    
    # VALIDACIÓN CLAVE FORÁNEA: Ver si hay empleados vinculados a esta área
    cursor.execute("SELECT COUNT(*) FROM empleados WHERE id_departamento = %s", (id_departamento,))
    empleados_vinculados = cursor.fetchone()[0]
    
    if empleados_vinculados > 0:
        flash(f"❌ No se puede eliminar el departamento. Tiene {empleados_vinculados} colaboradores asociados. Reubícalos antes de proceder.", "danger")
        cursor.close()
        return redirect("/departamentos")

    try:
        cursor.execute("DELETE FROM departamentos WHERE id_departamento = %s", (id_departamento,))
        mysql.connection.commit()
        flash("🗑️ El departamento sin operaciones ha sido eliminado del sistema.", "info")
    except Exception as e:
        mysql.connection.rollback()
        flash("❌ No se pudo completar la eliminación del área seleccionada.", "danger")
    finally:
        cursor.close()
    
    return redirect("/departamentos")