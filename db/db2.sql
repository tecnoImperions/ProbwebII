

-- =====================
-- Roles
-- =====================
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (nombre) VALUES
('admin'),
('trabajador'),
('usuario');

-- =====================
-- Usuarios
-- =====================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    rol_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- =====================
-- Tiendas / Sucursales
-- =====================
CREATE TABLE tiendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    usuario_admin_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_admin_id) REFERENCES usuarios(id)
);

-- =====================
-- Categorías de productos
-- =====================
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================
-- Productos
-- =====================
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado ENUM('disponible','vendido','agotado') DEFAULT 'disponible',
    tienda_id INT NOT NULL,
    categoria_id INT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tienda_id) REFERENCES tiendas(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- =====================
-- Clientes
-- =====================
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================
-- Pedidos
-- =====================
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    usuario_id INT NOT NULL, -- trabajador que procesa el pedido
    tienda_id INT NOT NULL,
    total DECIMAL(10,2) DEFAULT 0,
    estado ENUM('pendiente','enviado','entregado','cancelado') DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
);

-- =====================
-- Detalle de pedidos
-- =====================
CREATE TABLE pedido_detalle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);




ALTER TABLE productos
ADD precio DECIMAL(10,2) NOT NULL AFTER descripcion,
ADD imagen VARCHAR(255) AFTER precio;


INSERT INTO tiendas (nombre, direccion, usuario_admin_id)
VALUES ('Tienda Central', 'Av. Principal #123', 1);


ALTER TABLE productos
MODIFY usuario_id INT NULL;
ALTER TABLE productos
MODIFY estado ENUM('disponible','carrito','vendido','agotado')
DEFAULT 'disponible';

ALTER TABLE productos
ADD stock INT DEFAULT 0 AFTER precio;
