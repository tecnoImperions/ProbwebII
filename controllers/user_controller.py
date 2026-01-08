# controllers/user_controller.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.user import get_all_users

user_bp = Blueprint('user', __name__, template_folder='../templates')

# Listar todos los usuarios (solo admin)
@user_bp.route('/usuarios')
def listar_usuarios():
    if session.get('rol') != 'admin':
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('main.index'))
    
    usuarios = get_all_users()
    return render_template('usuarios.html', usuarios=usuarios)
