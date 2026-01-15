from db import get_db

# Ajustar stock manualmente
def actualizar_stock(producto_id, sucursal_id, nueva_cantidad):
    cn = get_db()
    cur = cn.cursor()
    cur.execute(
        "UPDATE stocks SET cantidad=%s WHERE producto_id=%s AND tienda_id=%s",
        (nueva_cantidad, producto_id, sucursal_id)
    )
    cn.commit()

# Obtener stock completo de un producto en todas las sucursales
def obtener_stock_producto_todas_sucursales(producto_id):
    cn = get_db()
    cur = cn.cursor(dictionary=True)
    cur.execute(
        "SELECT tienda_id, cantidad FROM stocks WHERE producto_id=%s",
        (producto_id,)
    )
    return cur.fetchall()
