from models.db import get_connection

def get_all_tiendas():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, t.nombre, t.direccion, u.nombre AS admin_nombre, t.fecha_creacion
        FROM tiendas t
        JOIN usuarios u ON t.usuario_admin_id = u.id
    """)
    tiendas = cursor.fetchall()
    cursor.close()
    db.close()
    return tiendas

def get_tienda_by_id(tienda_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tiendas WHERE id = %s", (tienda_id,))
    tienda = cursor.fetchone()
    cursor.close()
    db.close()
    return tienda

def create_tienda(nombre, direccion, usuario_admin_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO tiendas (nombre, direccion, usuario_admin_id)
        VALUES (%s, %s, %s)
    """, (nombre, direccion, usuario_admin_id))
    db.commit()
    cursor.close()
    db.close()
