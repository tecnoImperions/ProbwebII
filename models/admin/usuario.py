from models.db import get_connection
from hashlib import sha256
from datetime import datetime

# ===========================================
# Funciones básicas
# ===========================================

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def create_user(nombre, correo, password, rol_nombre='usuario'):
    db = get_connection()
    cursor = db.cursor()
    # Obtener el id del rol
    cursor.execute("SELECT id FROM roles WHERE nombre=%s", (rol_nombre,))
    rol = cursor.fetchone()
    if not rol:
        raise ValueError("Rol inválido")
    rol_id = rol[0]

    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password, rol_id, fecha_creacion) VALUES (%s, %s, %s, %s, %s)",
        (nombre, correo, hash_password(password), rol_id, datetime.now())
    )
    db.commit()
    cursor.close()
    db.close()

def get_all_usuarios():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.nombre, u.correo, r.nombre AS rol, u.fecha_creacion
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return [dict(id=row[0], nombre=row[1], correo=row[2], rol=row[3], fecha_creacion=row[4]) for row in rows]

def get_usuario_por_id(user_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.nombre, u.correo, r.nombre AS rol, u.fecha_creacion
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.id=%s
    """, (user_id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return dict(id=row[0], nombre=row[1], correo=row[2], rol=row[3], fecha_creacion=row[4])
    return None

def actualizar_usuario(user_id, nombre, correo, rol_nombre):
    db = get_connection()
    cursor = db.cursor()
    # Obtener id del rol
    cursor.execute("SELECT id FROM roles WHERE nombre=%s", (rol_nombre,))
    rol = cursor.fetchone()
    if not rol:
        raise ValueError("Rol inválido")
    rol_id = rol[0]

    cursor.execute(
        "UPDATE usuarios SET nombre=%s, correo=%s, rol_id=%s WHERE id=%s",
        (nombre, correo, rol_id, user_id)
    )
    db.commit()
    cursor.close()
    db.close()

def eliminar_usuario(user_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
    db.commit()
    cursor.close()
    db.close()

def cambiar_rol_usuario(user_id):
    db = get_connection()
    cursor = db.cursor()
    usuario = get_usuario_por_id(user_id)
    if not usuario:
        return
    # Alternar entre roles: usuario → trabajador → admin → usuario
    roles = ['usuario', 'trabajador', 'admin']
    next_rol = roles[(roles.index(usuario['rol']) + 1) % len(roles)]

    # Obtener id del siguiente rol
    cursor.execute("SELECT id FROM roles WHERE nombre=%s", (next_rol,))
    rol = cursor.fetchone()
    if not rol:
        return
    rol_id = rol[0]

    cursor.execute("UPDATE usuarios SET rol_id=%s WHERE id=%s", (rol_id, user_id))
    db.commit()
    cursor.close()
    db.close()
