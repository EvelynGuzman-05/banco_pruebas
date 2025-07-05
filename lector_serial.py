import serial
from datetime import datetime





class LectorSerial:
    def __init__(self, puerto, baudios, id_lanzamiento, buffer_size=100):
        try:
            self.puerto = serial.Serial(puerto, baudios, timeout=1)
           # self.puerto = SimuladorSerial() 
        except Exception as e:
         print(f"Error al usar el simulador serial: {e}")
        self.puerto = None
        #self.bd = gestor_bd
        self.id_lanzamiento = id_lanzamiento
        self.buffer_size = buffer_size
        self.buffer_datos = []

    def leer_dato(self):
        if not self.puerto or not self.puerto.is_open:
            return
        try:
            linea = self.puerto.readline().decode('utf-8', errors='ignore').strip()
            print(f"Linea leída: {linea}")  # Debugging line
            # Cambiar ruta del archivo aqui!!!
            # Ejemplo: archivo = open(f'C:/Users/carlo/Documents/python/MisionJinne/datos_{archivo_nombre}.csv', 'a')
            # Lo ideal es que el archivo apunte hacia la carpeta MisionJinne pero puede ser cualquier otra parte
            archivo = open('C:/Users/eveli/Documents/datos_3.csv', 'a')
            archivo.write(linea)
            partes = linea.split(',')

            datos = {
                't': None, 'p': None, 'a': None,
                'ax': None, 'ay': None, 'az': None,
                'gx': None, 'gy': None, 'gz': None
            }

            for parte in partes:
                if parte.startswith("t"):
                    datos['t'] = float(parte[1:])
                elif parte.startswith("p"):
                    datos['p'] = float(parte[1:])
                elif parte.startswith("a") and not parte.startswith(("ax", "ay", "az")):
                    datos['a'] = float(parte[1:])
                elif parte.startswith("ax"):
                    datos['ax'] = float(parte[2:])
                elif parte.startswith("ay"):
                    datos['ay'] = float(parte[2:])
                elif parte.startswith("az"):
                    datos['az'] = float(parte[2:])
                elif parte.startswith("gx"):
                    datos['gx'] = float(parte[2:])
                elif parte.startswith("gy"):
                    datos['gy'] = float(parte[2:])
                elif parte.startswith("gz"):
                    datos['gz'] = float(parte[2:])

            if all(v is not None for v in datos.values()):
                self.bd.guardar_medicion(datos, self.id_lanzamiento)
                ahora = datetime.now().strftime("%H:%M:%S")
                fila = {"Hora": ahora, **datos}
                self.buffer_datos.append(fila)
                if len(self.buffer_datos) > self.buffer_size:
                    self.buffer_datos.pop(0)

        except Exception as e:
            print("Error leyendo desde el puerto serial:", e)

