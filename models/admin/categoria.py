from models.db import get_connection

def get_all_categorias():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()
    return categorias

def create_categoria(nombre):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
    db.commit()
    cursor.close()
    db.close()
