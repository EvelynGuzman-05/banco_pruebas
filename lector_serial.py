import serial
from datetime import datetime


class LectorSerial:
    #Función para inicializar el lector serial
    def __init__(self, puerto, baudios):
        self.puerto = serial.Serial(puerto, baudios, timeout=1)
       

    #Función para leer datos del puerto serial
    def leer_dato(self): 
        linea = self.puerto.readline().decode('utf-8', errors='ignore').strip() 
        #print("Linea leída:", linea)  
        partes = linea.split() 
        #print("Partes:", partes)  
        datos = { 
            'masa': float(partes[0]), 
            'empuje': float(partes[1])
            } 
        #print(partes[0])
        #print(partes[1])
        return datos

        

#Linea leída: ax0.01,ay0.04,az-0.99,gx-4.33,gy1.59,gz0.67,t31.05,p1010.63,a1.38
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.21,gy1.46,gz0.61,t31.06,p1010.67,a1.06
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.39,gy1.71,gz0.73,t31.07,p1010.68,a0.98
#Linea leída: ax0.01,ay0.04,az-1.01,gx-4.15,gy1.34,gz0.73,t31.05,p1010.64,a1.26
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.09,gy1.10,gz0.43,t31.05,p1010.66,a1.08
#Linea leída: ax0.01,ay0.03,az-1.00,gx-4.15,gy1.16,gz0.49,t31.04,p1010.66,a1.10
#Linea leída: ax0.01,ay0.04,az-1.00,gx-3.91,gy1.40,gz0.67,t31.04,p1010.62,a1.43
#Linea leída: ax0.00,ay0.03,az-1.00,gx-4.46,gy1.40,gz0.67,t31.05,p1010.62,a1.42

