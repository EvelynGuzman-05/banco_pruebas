import mysql.connector
from mysql.connector import Error

def probar_conexion(host, user, password, database, port=3306):
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            conexion.close()
            return True
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return False

# Cambiar los parámetros según la configuración
if __name__ == "__main__":
    probar_conexion(
        host="localhost",
        user="root",
        password="guzman",
        database="tiempo_real",
        port=3308
    )
