from models.db import get_connection

# =======================
# PRODUCTOS
# =======================

def get_productos_disponibles():
    """Obtener productos disponibles para todos los usuarios"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, 
               c.nombre AS categoria_nombre, 
               t.nombre AS tienda_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN tiendas t ON p.tienda_id = t.id
        WHERE (p.estado = 'disponible' OR p.estado = 1)
        ORDER BY p.fecha_creacion DESC
    """)

    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos


def get_productos_usuario(usuario_id, estado):
    """Obtener productos de un usuario por estado (carrito, vendido)"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, 
               c.nombre AS categoria_nombre, 
               t.nombre AS tienda_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN tiendas t ON p.tienda_id = t.id
        WHERE p.usuario_id = %s 
          AND p.estado = %s
        ORDER BY p.fecha_creacion DESC
    """, (usuario_id, estado))

    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos


def crear_producto(nombre, descripcion, precio, tienda_id, categoria_id=None, imagen=None):
    """Crear un nuevo producto disponible"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos
        (nombre, descripcion, estado, precio, tienda_id, categoria_id, usuario_id, imagen)
        VALUES (%s, %s, 'disponible', %s, %s, %s, NULL, %s)
    """, (nombre, descripcion, precio, tienda_id, categoria_id, imagen))

    conn.commit()
    cursor.close()
    conn.close()


def actualizar_estado_producto(producto_id, nuevo_estado, usuario_id=None):
    """Actualizar estado de un producto"""
    conn = get_connection()
    cursor = conn.cursor()

    if usuario_id:
        cursor.execute("""
            UPDATE productos
            SET estado = %s, usuario_id = %s
            WHERE id = %s
        """, (nuevo_estado, usuario_id, producto_id))
    else:
        cursor.execute("""
            UPDATE productos
            SET estado = %s, usuario_id = NULL
            WHERE id = %s
        """, (nuevo_estado, producto_id))

    conn.commit()
    cursor.close()
    conn.close()


def get_all_tiendas():
    """Obtener todas las tiendas"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tiendas")
    tiendas = cursor.fetchall()

    cursor.close()
    conn.close()
    return tiendas


# =======================
# CARRITO
# =======================

def agregar_producto_a_carrito(producto_id, usuario_id):
    """Agregar producto al carrito"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar que el producto esté disponible y no tenga dueño
        cursor.execute("""
            SELECT id
            FROM productos
            WHERE id = %s
              AND (estado = 'disponible' OR estado = 1)
              AND usuario_id IS NULL
        """, (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            return False

        # Agregar al carrito
        cursor.execute("""
            UPDATE productos
            SET estado = 'carrito', usuario_id = %s
            WHERE id = %s
        """, (usuario_id, producto_id))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error al agregar al carrito: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def obtener_carrito_usuario(usuario_id):
    """Obtener productos en carrito de un usuario"""
    return get_productos_usuario(usuario_id, 'carrito')


def calcular_total_carrito(usuario_id):
    """Calcular total del carrito"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT SUM(precio) AS total
        FROM productos
        WHERE usuario_id = %s
          AND estado = 'carrito'
    """, (usuario_id,))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return float(resultado['total']) if resultado and resultado['total'] else 0.0


def eliminar_producto_carrito(producto_id, usuario_id):
    """Eliminar producto del carrito"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE productos
            SET estado = 'disponible', usuario_id = NULL
            WHERE id = %s
              AND usuario_id = %s
              AND estado = 'carrito'
        """, (producto_id, usuario_id))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar del carrito: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def vaciar_carrito(usuario_id):
    """Vaciar carrito del usuario"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE productos
            SET estado = 'disponible', usuario_id = NULL
            WHERE usuario_id = %s
              AND estado = 'carrito'
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