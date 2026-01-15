# models/cliente/stock.py
from models.db import get_connection

def obtener_stock_producto_sucursal(producto_id, tienda_id):
    """Obtener stock disponible de un producto en una tienda"""
    cn = get_connection()
    cursor = cn.cursor(dictionary=True)
    cursor.execute(
        "SELECT cantidad FROM productos_stock WHERE producto_id=%s AND tienda_id=%s",
        (producto_id, tienda_id)
    )
    resultado = cursor.fetchone()
    cursor.close()
    cn.close()
    return resultado['cantidad'] if resultado else 0

def descontar_stock_producto(producto_id, tienda_id, cantidad):
    """Descontar stock de un producto, devuelve False si no hay suficiente"""
    cn = get_connection()
    cursor = cn.cursor()
    
    cursor.execute(
        "SELECT cantidad FROM productos_stock WHERE producto_id=%s AND tienda_id=%s",
        (producto_id, tienda_id)
    )
    stock = cursor.fetchone()
    if not stock or stock[0] < cantidad:
        cursor.close()
        cn.close()
        return False
    
    cursor.execute(
        "UPDATE productos_stock SET cantidad = cantidad - %s WHERE producto_id=%s AND tienda_id=%s",
        (cantidad, producto_id, tienda_id)
    )
    cn.commit()
    cursor.close()
    cn.close()
    return True
