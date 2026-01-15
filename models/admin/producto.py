from models.db import get_connection

def get_all_productos():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.estado,
               t.nombre AS tienda_nombre, u.nombre AS usuario_nombre, p.fecha_creacion
        FROM productos p
        JOIN tiendas t ON p.tienda_id = t.id
        JOIN usuarios u ON p.usuario_id = u.id
    """)
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return productos

def get_productos_disponibles_count():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos WHERE estado='disponible'")
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return count

def create_producto(nombre, descripcion, estado, tienda_id, usuario_id, categoria_id=None):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, estado, tienda_id, usuario_id, categoria_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, descripcion, estado, tienda_id, usuario_id, categoria_id))
    db.commit()
    cursor.close()
    db.close()

def update_estado_producto(producto_id, estado):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE productos SET estado=%s WHERE id=%s", (estado, producto_id))
    db.commit()
    cursor.close()
    db.close()
