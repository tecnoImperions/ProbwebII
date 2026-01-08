# models/tienda.py
from models.db import get_connection

# Crear una nueva tienda (solo admin)
def crear_tienda(nombre, direccion, usuario_admin_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tiendas (nombre, direccion, usuario_admin_id) VALUES (%s,%s,%s)",
        (nombre, direccion, usuario_admin_id)
    )
    db.commit()
    cursor.close()
    db.close()

# Obtener todas las tiendas
def get_todas_las_tiendas():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT t.*, u.nombre AS admin_nombre FROM tiendas t "
        "JOIN usuarios u ON t.usuario_admin_id = u.id "
        "ORDER BY t.id"
    )
    tiendas = cursor.fetchall()
    cursor.close()
    db.close()
    return tiendas

# Obtener tienda por ID
def get_tienda_por_id(tienda_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT t.*, u.nombre AS admin_nombre FROM tiendas t "
        "JOIN usuarios u ON t.usuario_admin_id = u.id "
        "WHERE t.id=%s",
        (tienda_id,)
    )
    tienda = cursor.fetchone()
    cursor.close()
    db.close()
    return tienda

# Actualizar información de una tienda
def actualizar_tienda(tienda_id, nombre=None, direccion=None):
    db = get_connection()
    cursor = db.cursor()
    updates = []
    params = []
    
    if nombre:
        updates.append("nombre=%s")
        params.append(nombre)
    if direccion:
        updates.append("direccion=%s")
        params.append(direccion)
    
    if updates:
        query = "UPDATE tiendas SET " + ", ".join(updates) + " WHERE id=%s"
        params.append(tienda_id)
        cursor.execute(query, tuple(params))
        db.commit()
    
    cursor.close()
    db.close()

# Eliminar tienda (solo admin)
def eliminar_tienda(tienda_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tiendas WHERE id=%s", (tienda_id,))
    db.commit()
    cursor.close()
    db.close()
