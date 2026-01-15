-- =====================
-- AGREGAR TABLA DE STOCK
-- =====================
CREATE TABLE productos_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tienda_id INT NOT NULL,
    cantidad INT DEFAULT 0,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (tienda_id) REFERENCES tiendas(id),
    UNIQUE KEY unique_producto_tienda (producto_id, tienda_id)
);

-- =====================
-- CREAR TABLA DE CARRITO
-- =====================
CREATE TABLE carrito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT DEFAULT 1,
    tienda_id INT NOT NULL,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (tienda_id) REFERENCES tiendas(id),
    UNIQUE KEY unique_usuario_producto (usuario_id, producto_id)
);

-- =====================
-- MODIFICAR TABLA PRODUCTOS
-- =====================
-- Ya NO usamos usuario_id para carrito
ALTER TABLE productos 
DROP COLUMN usuario_id;

-- Estado solo para inventario
ALTER TABLE productos
MODIFY estado ENUM('disponible','agotado') DEFAULT 'disponible';

-- =====================
-- DATOS DE EJEMPLO
-- =====================
-- Insertar stock inicial para productos existentes
INSERT INTO productos_stock (producto_id, tienda_id, cantidad)
SELECT id, tienda_id, 10 
FROM productos
ON DUPLICATE KEY UPDATE cantidad = 10;