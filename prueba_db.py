import sqlite3

conn = sqlite3.connect("datos.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM dato")
filas = cursor.fetchall()

#print("Total de filas guardadas:", len(filas))
for fila in filas:
    print(fila)

conn.close()
