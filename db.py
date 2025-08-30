import sqlite3
from datetime import datetime


class BaseDatos:
    # Función para inicializar la base de datos
    def __init__(self, nombre_archivo="datos_prueba_durabilidad.db"):
        self.conn = sqlite3.connect(nombre_archivo)
        self.cursor = self.conn.cursor()
        self.crear_tabla()


    # Función para crear la tabla si no existe
    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dato (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperatura REAL,
                presion REAL,
                altitud REAL,
                aceleracion_x REAL,
                aceleracion_y REAL,
                aceleracion_z REAL,
                giroscopio_x REAL,
                giroscopio_y REAL,
                giroscopio_z REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()


    # Función para insertar un dato en la base de datos
    def insertar_dato(self, datos):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Hora local
            self.cursor.execute('''
                INSERT INTO dato (
                    temperatura, presion, altitud,
                    aceleracion_x, aceleracion_y, aceleracion_z,
                    giroscopio_x, giroscopio_y, giroscopio_z,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos.get('t'),
                datos.get('p'),
                datos.get('a'),
                datos.get('ax'),
                datos.get('ay'),
                datos.get('az'),
                datos.get('gx'),
                datos.get('gy'),
                datos.get('gz'),
                timestamp
            ))
            self.conn.commit()
        except Exception as e:
            print("Error al insertar en la base de datos:", e)

