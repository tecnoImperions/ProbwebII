import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="Juanc101.mysql.pythonanywhere-services.com",
        user="Juanc101",
        password="Juan#8913394",
        database="Juanc101$default"
    )
    
    cursor = conn.cursor()
    cursor.execute("SET time_zone = '-04:00'")  # Bolivia UTC-4
    cursor.close()
    
    return conn
