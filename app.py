from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from utils.auth_utils import login_user, logout_user, current_user

# =====================
# MODELOS
# =====================

# Usuarios
from models.user import create_user, get_user_by_email, hash_password

# Productos (CLIENTE)
from models.cliente.producto import get_productos_disponibles

# Carrito (CLIENTE) - NUEVO SISTEMA
from models.cliente.carrito import (
    agregar_producto_a_carrito,
    obtener_carrito_usuario,
    calcular_total_carrito,
    actualizar_cantidad_carrito,
    eliminar_producto_carrito,
    vaciar_carrito
)

# Pedidos (CLIENTE)
from models.cliente.pedido import (
    crear_pedido_desde_carrito,
    obtener_pedidos_usuario,
    obtener_detalle_pedido,
    cancelar_pedido
)

# Cliente
from models.cliente.cliente import obtener_cliente_por_usuario

# Pedidos Admin/Trabajador
from models.admin.pedido import (
    obtener_todos_pedidos,
    actualizar_estado_pedido,
    obtener_detalle_pedido_admin
)

# Admin
from models.admin.usuario import get_all_usuarios
from models.admin.tienda import get_all_tiendas as admin_get_all_tiendas
from models.admin.producto import get_all_productos
from models.cliente.usuario import get_all_clientes

# =====================
# CONFIG
# =====================
app = Flask(__name__)
app.secret_key = "mi_clave_secreta_super_segura_2024"

# =====================
# HOME PÚBLICO (LANDING PAGE)
# =====================
@app.route('/')
def index():
    return render_template('public/index.html')

# =====================
# DASHBOARD (Redirige según rol)
# =====================
@app.route('/dashboard')
def home():
    user = current_user()
    if not user:
        return redirect(url_for('index'))

    if user['rol'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user['rol'] == 'trabajador':
        return redirect(url_for('trabajador_dashboard'))
    else:
        return redirect(url_for('cliente_dashboard'))

# =====================
# AUTH
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

        if get_user_by_email(correo):
            return render_template('auth/register.html', error="El correo ya está registrado")

        create_user(nombre, correo, password)
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        user = get_user_by_email(correo)
        if user and user['password'] == hash_password(password):
            login_user(user)
            return redirect(url_for('home'))

        return render_template('auth/login.html', error="Credenciales incorrectas")

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# =====================
# DASHBOARD CLIENTE
# =====================
@app.route('/cliente')
def cliente_dashboard():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    disponible = get_productos_disponibles()
    carrito = obtener_carrito_usuario(user['id'])

    return render_template(
        'cliente/index.html',
        user=user,
        disponible=disponible,
        carrito=carrito
    )

# =====================
# CLIENTE: PRODUCTOS
# =====================
@app.route('/cliente/productos')
def cliente_productos():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    disponible = get_productos_disponibles()
    return render_template(
        'cliente/productos.html',
        user=user,
        disponible=disponible
    )

# =====================
# CLIENTE: CARRITO
# =====================
@app.route('/cliente/carrito')
def cliente_carrito():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    carrito = obtener_carrito_usuario(user['id'])
    total = calcular_total_carrito(user['id'])

    return render_template(
        'cliente/carrito.html',
        user=user,
        carrito=carrito,
        total=total
    )


@app.route('/cliente/agregar-carrito', methods=['POST'])
def cliente_agregar_carrito():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)

    if not producto_id:
        return jsonify({'success': False, 'message': 'Producto no especificado'}), 400

    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            return jsonify({'success': False, 'message': 'Cantidad debe ser mayor a 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Cantidad inválida'}), 400

    success, mensaje = agregar_producto_a_carrito(
        producto_id=producto_id,
        usuario_id=user['id'],
        tienda_id=1,
        cantidad=cantidad
    )

    if success:
        carrito = obtener_carrito_usuario(user['id'])
        total = calcular_total_carrito(user['id'])
        return jsonify({
            'success': True,
            'message': mensaje,
            'carrito_count': len(carrito),
            'total': total
        })
    else:
        return jsonify({'success': False, 'message': mensaje}), 400


@app.route('/cliente/carrito/actualizar', methods=['POST'])
def cliente_actualizar_cantidad():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json()
    carrito_id = data.get('carrito_id')
    nueva_cantidad = data.get('cantidad')

    if not carrito_id or nueva_cantidad is None:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

    try:
        nueva_cantidad = int(nueva_cantidad)
        if nueva_cantidad < 0:
            return jsonify({'success': False, 'message': 'Cantidad inválida'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Cantidad debe ser un número'}), 400

    success, mensaje = actualizar_cantidad_carrito(carrito_id, user['id'], nueva_cantidad)

    if success:
        total = calcular_total_carrito(user['id'])
        carrito = obtener_carrito_usuario(user['id'])
        return jsonify({
            'success': True,
            'message': mensaje,
            'total': total,
            'carrito_count': len(carrito)
        })
    else:
        return jsonify({'success': False, 'message': mensaje}), 400


@app.route('/cliente/carrito/eliminar/<int:carrito_id>', methods=['POST'])
def cliente_eliminar_carrito(carrito_id):
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    success, mensaje = eliminar_producto_carrito(carrito_id, user['id'])
    if not success:
        print(f"Error al eliminar: {mensaje}")
    return redirect(url_for('cliente_carrito'))


@app.route('/cliente/carrito/vaciar', methods=['POST'])
def cliente_vaciar_carrito():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    vaciar_carrito(user['id'])
    return redirect(url_for('cliente_carrito'))


@app.route('/cliente/carrito/comprar', methods=['POST'])
def cliente_finalizar_compra():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    carrito = obtener_carrito_usuario(user['id'])
    if not carrito:
        return redirect(url_for('cliente_carrito'))

    pedido_id, mensaje = crear_pedido_desde_carrito(user['id'], tienda_id=1)
    if pedido_id:
        flash("Pedido creado exitosamente", "success")
        return redirect(url_for('cliente_pedidos'))
    else:
        flash(f"Error al crear pedido: {mensaje}", "error")
        return redirect(url_for('cliente_carrito'))

# =====================
# CLIENTE: PEDIDOS
# =====================
@app.route('/cliente/pedidos')
def cliente_pedidos():
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    pedidos = obtener_pedidos_usuario(user['id'])
    return render_template('cliente/pedidos.html', user=user, pedidos=pedidos)


@app.route('/cliente/pedidos/<int:pedido_id>')
def cliente_ver_pedido(pedido_id):
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    pedido = obtener_detalle_pedido(pedido_id, user['id'])
    if not pedido:
        return "Pedido no encontrado", 404

    return render_template('cliente/pedido_detalle.html', user=user, pedido=pedido)


@app.route('/cliente/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
def cliente_cancelar_pedido(pedido_id):
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    success, mensaje = cancelar_pedido(pedido_id, user['id'])
    if not success:
        flash(f"Error al cancelar pedido: {mensaje}", "error")
    else:
        flash("Pedido cancelado exitosamente", "success")

    return redirect(url_for('cliente_pedidos'))


# =====================
# CLIENTE: IMPRIMIR COMPROBANTE
# =====================
@app.route('/cliente/pedido/<int:pedido_id>/imprimir')
def cliente_imprimir_comprobante(pedido_id):
    """Vista optimizada para imprimir comprobante"""
    user = current_user()
    if not user or user['rol'] != 'usuario':
        return redirect(url_for('login'))

    pedido = obtener_detalle_pedido(pedido_id, user['id'])
    if not pedido:
        return "Pedido no encontrado", 404

    return render_template('cliente/comprobante_imprimir.html', user=user, pedido=pedido)


# =====================
# DASHBOARD ADMIN
# =====================
@app.route('/admin')
def admin_dashboard():
    user = current_user()
    if not user or user['rol'] != 'admin':
        return redirect(url_for('login'))

    usuarios = get_all_usuarios()
    tiendas = admin_get_all_tiendas()
    productos = get_all_productos()
    clientes = get_all_clientes()

    return render_template(
        'admin/dashboard.html',
        user=user,
        usuarios=usuarios,
        tiendas=tiendas,
        productos=productos,
        clientes=clientes
    )


# =====================
# ADMIN / TRABAJADOR: PEDIDOS
# =====================
@app.route('/admin/pedidos')
def admin_pedidos():
    user = current_user()
    if not user or user['rol'] not in ['admin', 'trabajador']:
        return "No autorizado", 403

    pedidos = obtener_todos_pedidos()
    return render_template("admin/pedidos.html", user=user, pedidos=pedidos)


@app.route('/admin/pedidos/<int:pedido_id>/estado', methods=['POST'])
def admin_actualizar_estado_pedido(pedido_id):
    user = current_user()
    if not user or user['rol'] not in ['admin', 'trabajador']:
        return "No autorizado", 403

    nuevo_estado = request.form.get('estado')
    if nuevo_estado not in ['pendiente', 'enviado', 'entregado', 'cancelado']:
        return "Estado inválido", 400

    actualizar_estado_pedido(pedido_id, nuevo_estado)
    return redirect(url_for('admin_pedidos'))


@app.route('/trabajador')
def trabajador_dashboard():
    user = current_user()
    if not user or user['rol'] != 'trabajador':
        return redirect(url_for('login'))

    pedidos = obtener_todos_pedidos()
    return render_template("trabajador/pedidos.html", user=user, pedidos=pedidos)


# =====================
# MANEJO DE ERRORES
# =====================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500


# =====================
# CONTEXTO GLOBAL
# =====================
@app.context_processor
def inject_user():
    return dict(current_user=current_user())


# =====================
# RUN
# =====================
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)