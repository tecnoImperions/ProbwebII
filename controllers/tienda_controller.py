# controllers/tienda_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.tienda import crear_tienda, get_todas_las_tiendas, actualizar_tienda, eliminar_tienda

tienda_bp = Blueprint('tienda', __name__, template_folder='../templates')

# Listar tiendas
@tienda_bp.route('/tiendas')
def listar_tiendas():
    tiendas = get_todas_las_tiendas()
    return render_template('tiendas.html', tiendas=tiendas)

# Crear tienda
@tienda_bp.route('/tiendas/nueva', methods=['GET', 'POST'])
def nueva_tienda():
    if session.get('rol') != 'admin':
        flash("Solo el admin puede crear tiendas", "danger")
        return redirect(url_for('tienda.listar_tiendas'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        usuario_admin_id = session.get('user_id')
        
        crear_tienda(nombre, direccion, usuario_admin_id)
        flash("Tienda creada correctamente", "success")
        return redirect(url_for('tienda.listar_tiendas'))
    
    return render_template('nueva_tienda.html')

# Editar tienda
@tienda_bp.route('/tiendas/<int:id>/editar', methods=['POST'])
def editar_tienda(id):
    if session.get('rol') != 'admin':
        flash("Solo el admin puede editar tiendas", "danger")
        return redirect(url_for('tienda.listar_tiendas'))
    
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    actualizar_tienda(id, nombre, direccion)
    flash("Tienda actualizada", "success")
    return redirect(url_for('tienda.listar_tiendas'))

# Eliminar tienda
@tienda_bp.route('/tiendas/<int:id>/eliminar', methods=['POST'])
def borrar_tienda(id):
    if session.get('rol') != 'admin':
        flash("Solo el admin puede eliminar tiendas", "danger")
        return redirect(url_for('tienda.listar_tiendas'))
    
    eliminar_tienda(id)
    flash("Tienda eliminada", "success")
    return redirect(url_for('tienda.listar_tiendas'))
