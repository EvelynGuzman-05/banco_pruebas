import mysql.connector
from mysql.connector import Error

class BaseDatos:
    def __init__(self, host, user, password, database, port='3306'):
        try:
            print("Entro db")
            self.conexion = mysql.connector.connect(
                print("Intentando conectar a la base de datos..."),
                host=host,
                port=port,
                user=user,  
                password=password,
                database=database
                
            )
            print("Si conecto la bd")
        except:
            print(f"Error al conectar a la base de datos:")
            self.conexion = None

    def guardar_medicion(self, datos, id_lanzamiento):
        if self.conexion is None:
            print("No hay conexión con la base de datos.")
            return

        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                INSERT INTO mediciones (
                    tiempo, temperatura, presion, altitud,
                    aceleracion_x, aceleracion_y, aceleracion_z,
                    giroscopio_x, giroscopio_y, giroscopio_z, id_lanzamiento
                ) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datos['t'], datos['p'], datos['a'],
                datos['ax'], datos['ay'], datos['az'],
                datos['gx'], datos['gy'], datos['gz'],
                id_lanzamiento
            ))
            self.conexion.commit()
            print("Medición guardada correctamente")
        except Exception as e:
            print("Error al guardar en la base de datos:", e)
