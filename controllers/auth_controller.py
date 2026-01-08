# controllers/auth_controller.py
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from models.user import create_user, get_user_by_email, hash_password

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# Registro de usuario
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        rol_id = 3  # Usuario normal por defecto
        
        existing = get_user_by_email(correo)
        if existing:
            flash("El correo ya está registrado", "danger")
            return redirect(url_for('auth.register'))
        
        create_user(nombre, correo, password, rol_id)
        flash("Usuario registrado correctamente", "success")
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        user = get_user_by_email(correo)
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['rol'] = user['rol']
            flash("Bienvenido, " + user['nombre'], "success")
            return redirect(url_for('main.index'))
        else:
            flash("Correo o contraseña incorrecta", "danger")
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('auth.login'))
