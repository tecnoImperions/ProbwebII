import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="probwebii"
    )
    
    cursor = conn.cursor()
    cursor.execute("SET time_zone = '-04:00'")  # Bolivia UTC-4
    cursor.close()
    
    return conn
