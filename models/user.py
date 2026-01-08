from models.db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(nombre, correo, password, rol_id=3):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password, rol_id) VALUES (%s,%s,%s,%s)",
        (nombre, correo, hashed, rol_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_email(correo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT u.*, r.nombre AS rol FROM usuarios u JOIN roles r ON u.rol_id=r.id WHERE correo=%s", (correo,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT u.*, r.nombre AS rol FROM usuarios u JOIN roles r ON u.rol_id=r.id ORDER BY u.id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users
