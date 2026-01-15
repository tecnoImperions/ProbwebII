# models/admin/pedido.py
from models.db import get_connection

def obtener_todos_pedidos():
    """Obtener todos los pedidos con sus detalles (para admin/trabajador)"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.cliente_id,
                p.usuario_id,
                p.tienda_id,
                p.total,
                p.estado,
                p.fecha_creacion,
                c.nombre AS cliente_nombre,
                c.correo AS cliente_correo,
                t.nombre AS tienda_nombre,
                u.nombre AS usuario_nombre,
                COUNT(pd.id) AS cantidad_productos
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN tiendas t ON p.tienda_id = t.id
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            LEFT JOIN pedido_detalle pd ON pd.pedido_id = p.id
            GROUP BY p.id
            ORDER BY p.fecha_creacion DESC
        """)
        
        pedidos = cursor.fetchall()
        return pedidos
        
    except Exception as e:
        print(f"Error al obtener todos los pedidos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def obtener_detalle_pedido_admin(pedido_id):
    """Obtener detalles completos de un pedido (para admin/trabajador)"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Datos del pedido
        cursor.execute("""
            SELECT 
                p.id,
                p.tienda_id,
                p.total,
                p.estado,
                p.fecha_creacion,
                t.nombre AS tienda_nombre,
                c.nombre AS cliente_nombre,
                c.correo AS cliente_correo,
                c.telefono AS cliente_telefono,
                u.nombre AS usuario_nombre
            FROM pedidos p
            LEFT JOIN tiendas t ON p.tienda_id = t.id
            LEFT JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.id=%s
        """, (pedido_id,))
        
        pedido = cursor.fetchone()
        
        if not pedido:
            return None
        
        # Productos del pedido
        cursor.execute("""
            SELECT 
                pd.producto_id,
                pd.cantidad,
                pd.precio_unitario,
                pr.nombre AS producto_nombre,
                pr.imagen AS producto_imagen,
                (pd.cantidad * pd.precio_unitario) AS subtotal
            FROM pedido_detalle pd
            JOIN productos pr ON pr.id = pd.producto_id
            WHERE pd.pedido_id=%s
        """, (pedido_id,))
        
        pedido['productos'] = cursor.fetchall()
        
        return pedido
        
    except Exception as e:
        print(f"Error al obtener detalle del pedido: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def actualizar_estado_pedido(pedido_id, nuevo_estado):
    """Actualizar el estado de un pedido (para admin/trabajador)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE pedidos SET estado=%s WHERE id=%s",
            (nuevo_estado, pedido_id)
        )
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar estado del pedido: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_estadisticas_pedidos():
    """Obtener estadísticas de pedidos para dashboard admin"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_pedidos,
                SUM(CASE WHEN estado='pendiente' THEN 1 ELSE 0 END) AS pendientes,
                SUM(CASE WHEN estado='enviado' THEN 1 ELSE 0 END) AS enviados,
                SUM(CASE WHEN estado='entregado' THEN 1 ELSE 0 END) AS entregados,
                SUM(CASE WHEN estado='cancelado' THEN 1 ELSE 0 END) AS cancelados,
                SUM(CASE WHEN estado='entregado' THEN total ELSE 0 END) AS total_ventas
            FROM pedidos
        """)
        
        stats = cursor.fetchone()
        return stats
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return None
    finally:
        cursor.close()
        conn.close()