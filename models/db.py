import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="sql305.infinityfree.com",        # Host de InfinityFree
        user="if0_40092981",                   # Tu usuario MySQL
        password="zxiFMO8HMDeD",               # Tu contraseña
        database="if0_40092981_probwebii_db"  # Nombre de la base de datos
    )
