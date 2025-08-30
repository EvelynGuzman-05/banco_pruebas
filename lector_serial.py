import serial
from datetime import datetime


class LectorSerial:
    #Función para inicializar el lector serial
    def __init__(self, puerto, baudios, buffer_datos = []):
        self.puerto = serial.Serial(puerto, baudios, timeout=1)
        self.buffer_datos = buffer_datos


    #Función para leer datos del puerto serial
    def leer_dato(self):
        linea = self.puerto.readline().decode('utf-8', errors='ignore').strip()
        # print(f"{linea}")  # Debugging line
        # Cambiar ruta del archivo aqui!!!
        # Ejemplo: archivo = open(f'C:/Users/carlo/Documents/python/MisionJinne/datos_{archivo_nombre}.csv', 'a')
        # Lo ideal es que el archivo apunte hacia la carpeta MisionJinne pero puede ser cualquier otra parte
        #with open('C:/Users/eveli/Documents/datos_3.csv', 'a', encoding='utf-8') as archivo:
        #    archivo.write(linea + '\n')
        if not linea:
            return
        partes = linea.split(',')

        datos = {
            't': None, 'p': None, 'a': None,
            'ax': None, 'ay': None, 'az': None,
            'gx': None, 'gy': None, 'gz': None, 'e': None,
        }

        for parte in partes:
            try:
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
                elif parte.startswith("e"):
                    datos['e'] = int(parte[1:])
            except ValueError:
                # Si hay un dato corrupto, lo ignoramos
                continue
        self.buffer_datos.append(datos)

#Linea leída: ax0.01,ay0.04,az-0.99,gx-4.33,gy1.59,gz0.67,t31.05,p1010.63,a1.38
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.21,gy1.46,gz0.61,t31.06,p1010.67,a1.06
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.39,gy1.71,gz0.73,t31.07,p1010.68,a0.98
#Linea leída: ax0.01,ay0.04,az-1.01,gx-4.15,gy1.34,gz0.73,t31.05,p1010.64,a1.26
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.09,gy1.10,gz0.43,t31.05,p1010.66,a1.08
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.15,gy1.16,gz0.49,t31.04,p1010.66,a1.10
#Linea leída: ax0.01,ay0.04,az-1.00,gx-3.91,gy1.40,gz0.67,t31.04,p1010.62,a1.43
#Linea leída: ax0.00,ay0.03,az-1.00,gx-4.46,gy1.40,gz0.67,t31.05,p1010.62,a1.42