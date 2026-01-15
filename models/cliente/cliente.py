# models/cliente/cliente.py
from models.db import get_connection

def obtener_cliente_por_usuario(usuario_id):
    """Obtener cliente asociado a un usuario"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.id, c.nombre, c.correo
            FROM clientes c
            JOIN usuarios u ON u.correo = c.correo
            WHERE u.id=%s
        """, (usuario_id,))
        cliente = cursor.fetchone()
        return cliente
    except Exception as e:
        print(f"Error al obtener cliente: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
