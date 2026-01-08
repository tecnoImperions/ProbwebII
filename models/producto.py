# models/producto.py
from models.db import get_connection

# Obtener productos por estado y usuario (puede ser admin o trabajador)
def get_productos_por_estado(user_id=None, estado=None):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT p.*, t.nombre AS tienda_nombre, u.nombre AS usuario_nombre FROM productos p " \
            "JOIN tiendas t ON p.tienda_id = t.id " \
            "JOIN usuarios u ON p.usuario_id = u.id"
    
    params = []
    conditions = []
    
    if user_id:
        conditions.append("p.usuario_id=%s")
        params.append(user_id)
    if estado:
        conditions.append("p.estado=%s")
        params.append(estado)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY p.id"
    
    cursor.execute(query, tuple(params))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    return resultados

# Crear nuevo producto
def crear_producto(nombre, descripcion, estado, tienda_id, usuario_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, descripcion, estado, tienda_id, usuario_id) VALUES (%s,%s,%s,%s,%s)",
        (nombre, descripcion, estado, tienda_id, usuario_id)
    )
    db.commit()
    cursor.close()
    db.close()

# Actualizar estado de un producto
def actualizar_estado_producto(producto_id, estado):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE productos SET estado=%s WHERE id=%s",
        (estado, producto_id)
    )
    db.commit()
    cursor.close()
    db.close()

# Obtener producto por ID
def get_producto_by_id(producto_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, t.nombre AS tienda_nombre, u.nombre AS usuario_nombre FROM productos p "
        "JOIN tiendas t ON p.tienda_id = t.id "
        "JOIN usuarios u ON p.usuario_id = u.id "
        "WHERE p.id=%s",
        (producto_id,)
    )
    producto = cursor.fetchone()
    cursor.close()
    db.close()
    return producto
