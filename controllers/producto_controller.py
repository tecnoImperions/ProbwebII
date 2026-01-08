# controllers/producto_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.producto import crear_producto, get_productos_por_estado, actualizar_estado_producto

producto_bp = Blueprint('producto', __name__, template_folder='../templates')

# Ver productos
@producto_bp.route('/productos')
def listar_productos():
    estado = request.args.get('estado')
    user_id = session.get('user_id')
    
    productos = get_productos_por_estado(user_id=user_id, estado=estado)
    return render_template('productos.html', productos=productos)

# Crear producto
@producto_bp.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if session.get('rol') not in ['admin', 'trabajador']:
        flash("No tienes permisos para crear productos", "danger")
        return redirect(url_for('producto.listar_productos'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        estado = request.form['estado']
        tienda_id = request.form['tienda_id']
        usuario_id = session.get('user_id')
        
        crear_producto(nombre, descripcion, estado, tienda_id, usuario_id)
        flash("Producto creado correctamente", "success")
        return redirect(url_for('producto.listar_productos'))
    
    return render_template('nuevo_producto.html')

# Actualizar estado de producto
@producto_bp.route('/productos/<int:id>/estado', methods=['POST'])
def cambiar_estado_producto(id):
    nuevo_estado = request.form['estado']
    actualizar_estado_producto(id, nuevo_estado)
    flash("Estado actualizado", "success")
    return redirect(url_for('producto.listar_productos'))
