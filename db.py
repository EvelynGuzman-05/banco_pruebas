import sqlite3
from datetime import datetime


class BaseDatos:
    # Función para inicializar la base de datos
    def __init__(self, nombre_archivo="banco pruebas v4.db"):
        self.conn = sqlite3.connect(nombre_archivo)
        self.cursor = self.conn.cursor()
        self.crear_tabla()


    # Función para crear la tabla si no existe
    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dato (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                masa REAL,
                empuje REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()


    # Función para insertar un dato en la base de datos
    def insertar_dato(self, datos):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Hora local
            self.cursor.execute('''
                INSERT INTO dato (masa, empuje, timestamp) VALUES (?, ?, ?)
            ''', (
                datos.get('masa'),
                datos.get('empuje'),
                timestamp
            ))
            self.conn.commit()
        except Exception as e:
            print("Error al insertar en la base de datos:", e)

