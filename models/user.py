# models/user.py
from models.db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(correo):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.*, r.nombre AS rol 
        FROM usuarios u 
        JOIN roles r ON u.rol_id = r.id 
        WHERE correo=%s
    """, (correo,))
    return cursor.fetchone()

def create_user(nombre, correo, password, rol='usuario'):
    db = get_connection()
    cursor = db.cursor()
    hashed = hash_password(password)
    
    cursor.execute("SELECT id FROM roles WHERE nombre=%s", (rol,))
    rol_row = cursor.fetchone()
    rol_id = rol_row[0] if rol_row else 3

    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password, rol_id) VALUES (%s,%s,%s,%s)",
        (nombre, correo, hashed, rol_id)
    )
    db.commit()

def get_all_users():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id, u.nombre, u.correo, r.nombre AS rol 
        FROM usuarios u 
        JOIN roles r ON u.rol_id = r.id
    """)
    return cursor.fetchall()
