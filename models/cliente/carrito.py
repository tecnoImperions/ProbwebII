# models/cliente/carrito.py
from models.db import get_connection
from models.cliente.stock import obtener_stock_producto_sucursal

def agregar_producto_a_carrito(producto_id, usuario_id, tienda_id=1, cantidad=1):
    """Agregar producto al carrito verificando stock"""
    
    # 1. Verificar que hay stock suficiente
    stock_disponible = obtener_stock_producto_sucursal(producto_id, tienda_id)
    if stock_disponible < cantidad:
        return False, f"Stock insuficiente. Disponible: {stock_disponible}"
    
    # 2. Verificar que el producto existe y está disponible
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, nombre, estado 
            FROM productos 
            WHERE id=%s
        """, (producto_id,))
        
        producto = cursor.fetchone()
        if not producto:
            return False, "Producto no encontrado"
        
        if producto['estado'] != 'disponible':
            return False, "Producto no disponible"
        
        # 3. Verificar si ya está en el carrito
        cursor.execute("""
            SELECT id, cantidad 
            FROM carrito 
            WHERE usuario_id=%s AND producto_id=%s
        """, (usuario_id, producto_id))
        
        item_existente = cursor.fetchone()
        
        if item_existente:
            # Actualizar cantidad
            nueva_cantidad = item_existente['cantidad'] + cantidad
            
            # Validar que no exceda stock
            if nueva_cantidad > stock_disponible:
                return False, f"No puedes agregar más. Stock disponible: {stock_disponible}"
            
            cursor.execute("""
                UPDATE carrito 
                SET cantidad=%s 
                WHERE id=%s
            """, (nueva_cantidad, item_existente['id']))
        else:
            # Insertar nuevo item
            cursor.execute("""
                INSERT INTO carrito (usuario_id, producto_id, cantidad, tienda_id)
                VALUES (%s, %s, %s, %s)
            """, (usuario_id, producto_id, cantidad, tienda_id))
        
        conn.commit()
        return True, "Producto agregado al carrito"
        
    except Exception as e:
        conn.rollback()
        print(f"Error al agregar al carrito: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def obtener_carrito_usuario(usuario_id):
    """Obtener productos en carrito del usuario con información completa"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                c.id AS carrito_id,
                c.cantidad,
                p.id AS producto_id,
                p.nombre,
                p.descripcion,
                p.precio,
                p.imagen,
                p.stock,
                cat.nombre AS categoria_nombre,
                t.nombre AS tienda_nombre,
                (c.cantidad * p.precio) AS subtotal
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
            LEFT JOIN categorias cat ON p.categoria_id = cat.id
            LEFT JOIN tiendas t ON c.tienda_id = t.id
            WHERE c.usuario_id=%s
            ORDER BY c.fecha_agregado DESC
        """, (usuario_id,))
        
        carrito = cursor.fetchall()
        return carrito
        
    except Exception as e:
        print(f"Error al obtener carrito: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def calcular_total_carrito(usuario_id):
    """Calcular total del carrito"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT SUM(c.cantidad * p.precio) AS total
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id=%s
        """, (usuario_id,))
        
        resultado = cursor.fetchone()
        return float(resultado['total']) if resultado and resultado['total'] else 0.0
        
    except Exception as e:
        print(f"Error al calcular total: {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()


def actualizar_cantidad_carrito(carrito_id, usuario_id, nueva_cantidad):
    """Actualizar cantidad de un producto en el carrito"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener info del item
        cursor.execute("""
            SELECT c.producto_id, c.tienda_id
            FROM carrito c
            WHERE c.id=%s AND c.usuario_id=%s
        """, (carrito_id, usuario_id))
        
        item = cursor.fetchone()
        if not item:
            return False, "Item no encontrado"
        
        # Verificar stock
        stock = obtener_stock_producto_sucursal(item['producto_id'], item['tienda_id'])
        if nueva_cantidad > stock:
            return False, f"Stock insuficiente. Disponible: {stock}"
        
        if nueva_cantidad <= 0:
            return eliminar_producto_carrito(carrito_id, usuario_id)
        
        # Actualizar
        cursor.execute("""
            UPDATE carrito 
            SET cantidad=%s 
            WHERE id=%s AND usuario_id=%s
        """, (nueva_cantidad, carrito_id, usuario_id))
        
        conn.commit()
        return True, "Cantidad actualizada"
        
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar cantidad: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def eliminar_producto_carrito(carrito_id, usuario_id):
    """Eliminar producto del carrito"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM carrito
            WHERE id=%s AND usuario_id=%s
        """, (carrito_id, usuario_id))
        
        conn.commit()
        return True, "Producto eliminado"
        
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar del carrito: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def vaciar_carrito(usuario_id):
    """Vaciar todo el carrito del usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM carrito
            WHERE usuario_id=%s
        """, (usuario_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al vaciar carrito: {e}")
        return False
    finally:
        cursor.close()
        conn.close()