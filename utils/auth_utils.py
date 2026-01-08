from flask import session

def login_user(user_id):
    session['user_id'] = user_id

def logout_user():
    session.pop('user_id', None)

def current_user():
    return session.get('user_id')
