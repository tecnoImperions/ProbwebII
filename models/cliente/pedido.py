# models/cliente/pedido.py
from models.db import get_connection
from models.cliente.stock import descontar_stock_producto
from models.cliente.carrito import vaciar_carrito
from datetime import datetime

def crear_pedido_desde_carrito(usuario_id, tienda_id=1):
    """Crear pedido desde carrito descontando stock"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Obtener items del carrito
        cursor.execute("""
            SELECT c.id, c.producto_id, c.cantidad, p.nombre, p.precio
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id=%s AND c.tienda_id=%s
        """, (usuario_id, tienda_id))
        
        items_carrito = cursor.fetchall()
        if not items_carrito:
            return None, "El carrito está vacío"
        
        # 2. Calcular total
        total = sum(float(item['precio']) * item['cantidad'] for item in items_carrito)
        
        # 3. Obtener o crear cliente
        cursor.execute("""
            SELECT c.id FROM clientes c
            JOIN usuarios u ON c.correo = u.correo
            WHERE u.id=%s
        """, (usuario_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            cursor.execute("SELECT nombre, correo FROM usuarios WHERE id=%s", (usuario_id,))
            usuario = cursor.fetchone()
            cursor.execute(
                "INSERT INTO clientes (nombre, correo) VALUES (%s,%s)",
                (usuario['nombre'], usuario['correo'])
            )
            cliente_id = cursor.lastrowid
        else:
            cliente_id = cliente['id']
        
        # 4. Crear pedido
        cursor.execute("""
            INSERT INTO pedidos (cliente_id, usuario_id, tienda_id, total, estado, fecha_creacion)
            VALUES (%s,%s,%s,%s,'pendiente', NOW())
        """, (cliente_id, usuario_id, tienda_id, total))
        pedido_id = cursor.lastrowid
        
        # 5. Crear detalle y descontar stock
        for item in items_carrito:
            if not descontar_stock_producto(item['producto_id'], tienda_id, item['cantidad']):
                raise Exception(f"Stock insuficiente para {item['nombre']}")
            cursor.execute("""
                INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
                VALUES (%s,%s,%s,%s)
            """, (pedido_id, item['producto_id'], item['cantidad'], item['precio']))
        
        # 6. Vaciar carrito
        cursor.execute("DELETE FROM carrito WHERE usuario_id=%s", (usuario_id,))
        conn.commit()
        return pedido_id, "Pedido creado exitosamente"
        
    except Exception as e:
        conn.rollback()
        print(f"Error al crear pedido: {e}")
        return None, str(e)
    finally:
        cursor.close()
        conn.close()


def obtener_pedidos_usuario(usuario_id):
    """Obtener todos los pedidos de un usuario"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.tienda_id,
                p.total,
                p.estado,
                p.fecha_creacion,
                COUNT(pd.id) AS cantidad_productos
            FROM pedidos p
            LEFT JOIN pedido_detalle pd ON pd.pedido_id = p.id
            WHERE p.usuario_id=%s
            GROUP BY p.id
            ORDER BY p.fecha_creacion DESC
        """, (usuario_id,))
        
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener pedidos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def obtener_detalle_pedido(pedido_id, usuario_id):
    """Obtener detalles completos de un pedido"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.tienda_id,
                p.total,
                p.estado,
                p.fecha_creacion,
                t.nombre AS tienda_nombre,
                c.nombre AS cliente_nombre,
                c.correo AS cliente_correo
            FROM pedidos p
            LEFT JOIN tiendas t ON p.tienda_id = t.id
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE p.id=%s AND p.usuario_id=%s
        """, (pedido_id, usuario_id))
        
        pedido = cursor.fetchone()
        if not pedido:
            return None
        
        cursor.execute("""
            SELECT 
                pd.producto_id,
                pd.cantidad,
                pd.precio_unitario,
                pr.nombre AS producto_nombre,
                pr.imagen AS producto_imagen
            FROM pedido_detalle pd
            JOIN productos pr ON pr.id = pd.producto_id
            WHERE pd.pedido_id=%s
        """, (pedido_id,))
        
        pedido['productos'] = cursor.fetchall()
        return pedido
    except Exception as e:
        print(f"Error al obtener detalle: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def cancelar_pedido(pedido_id, usuario_id):
    """Cancelar pedido y devolver stock"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, tienda_id, estado
            FROM pedidos 
            WHERE id=%s AND usuario_id=%s
        """, (pedido_id, usuario_id))
        
        pedido = cursor.fetchone()
        if not pedido:
            return False, "Pedido no encontrado"
        if pedido['estado'] != 'pendiente':
            return False, "Solo se pueden cancelar pedidos pendientes"
        
        tienda_id = pedido['tienda_id']
        
        cursor.execute("""
            SELECT producto_id, cantidad 
            FROM pedido_detalle 
            WHERE pedido_id=%s
        """, (pedido_id,))
        productos = cursor.fetchall()
        
        for p in productos:
            cursor.execute("""
                UPDATE productos_stock 
                SET cantidad = cantidad + %s 
                WHERE producto_id=%s AND tienda_id=%s
            """, (p['cantidad'], p['producto_id'], tienda_id))
        
        cursor.execute("""
            UPDATE pedidos 
            SET estado='cancelado' 
            WHERE id=%s
        """, (pedido_id,))
        conn.commit()
        return True, "Pedido cancelado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al cancelar pedido: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()