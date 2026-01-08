# models/db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # tu contraseña de XAMPP
        database="probwebii"
    )
