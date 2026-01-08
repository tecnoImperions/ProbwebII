from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from models.user import create_user, get_user_by_email, hash_password
from models.producto import (
    get_productos_por_estado, 
    crear_producto, 
    actualizar_estado_producto
)
from utils.auth_utils import login_user, logout_user, current_user

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"  # Cambiar por algo más seguro en producción

# =====================
# Rutas Auth
# =====================

@app.route('/')
def home():
    if not current_user():
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

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
            login_user(user['id'])
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html', error="Correo o contraseña incorrectos")
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# =====================
# Dashboard
# =====================

@app.route('/dashboard')
def dashboard():
    if not current_user():
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Ajustar a estados válidos de MySQL: disponible / vendido / agotado
    disponible = get_productos_por_estado(user_id, 'disponible')
    vendido = get_productos_por_estado(user_id, 'vendido')
    agotado = get_productos_por_estado(user_id, 'agotado')

    return render_template('index.html', disponible=disponible, vendido=vendido, agotado=agotado)

# =====================
# Productos
# =====================

@app.route('/productos/nuevo', methods=['POST'])
def crear_producto_route():
    if not current_user():
        return redirect(url_for('login'))

    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    tienda_id = request.form.get('tienda_id')  # Obligatorio
    estado = 'disponible'
    usuario_id = session['user_id']

    if not tienda_id:
        return "Error: debe seleccionar una tienda", 400

    crear_producto(nombre, descripcion, estado, int(tienda_id), usuario_id)
    return redirect(url_for('dashboard'))

@app.route('/productos/<int:id>/estado', methods=['POST'])
def update_estado(id):
    if not current_user():
        return jsonify({"error": "No autorizado"}), 401

    nuevo_estado = request.form.get('estado')
    if nuevo_estado not in ['disponible', 'vendido', 'agotado']:
        return jsonify({"error": "Estado inválido"}), 400

    actualizar_estado_producto(id, nuevo_estado)
    return jsonify({"success": True})

# =====================
# Ejecutar Flask
# =====================
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
