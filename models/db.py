import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="Juanc101.mysql.pythonanywhere-services.com",
        user="Juanc101",
        password="Juan#8913394",
        database="Juanc101$default"
    )
