from flask import session

# Guardar usuario completo en sesión
def login_user(user):
    session['user'] = user

# Borrar sesión
def logout_user():
    session.pop('user', None)

# Retornar usuario actual
def current_user():
    return session.get('user')
