
# Importación de librerías
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QGridLayout, QStackedLayout, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from db import BaseDatos
from lector_serial import LectorSerial
from datetime import datetime

# NOTA:Constructor --> Es un método especial de una clase que se llama automáticamente cuando creas un objeto de esa clase
# Cada clase que necesita atributos para funcionar correctamente suele tener un constructor (__init__).
# Cuando creas una instancia de esa clase, el constructor se ejecuta automáticamente y todos los atributos necesarios se inicializan.

class GraficaExpandible(QWidget):
    def __init__(self, titulo, obtener_datos_callback, regresar_callback):
        super().__init__()
        
        self.obtener_datos = obtener_datos_callback

        layout = QVBoxLayout()
        self.setLayout(layout)

        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setAlignment(Qt.AlignCenter)
        etiqueta_titulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        layout.addWidget(etiqueta_titulo)

        self.figura = plt.figure(facecolor="#3d3d3d")
        self.canvas = FigureCanvas(self.figura)
        layout.addWidget(self.canvas)

        boton_regresar = QPushButton("← REGRESAR")
        boton_regresar.setStyleSheet("background-color: #A6FF47; font-size: 16px; padding: 10px;")
        boton_regresar.clicked.connect(regresar_callback)

        layout.addWidget(boton_regresar)

    def actualizar(self):
        x, y = self.obtener_datos()
        if x.empty or y.empty:
            return
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.plot(x, y, color='white')
        ax.set_facecolor("#3d3d3d")
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        self.figura.tight_layout()
        self.canvas.draw()

class VentanaPrincipal(QMainWindow):
    #Función para inicializar la ventana principal
    def __init__(self, lector_serial):
        super().__init__()
        self.db = BaseDatos()  # Aquí, self.db es una variable que pertenece a esta instancia
        self.ultimo_guardado = 0
        self.lector_serial = lector_serial
        self.indice_actual = 0
        self.grafica_expandida = None
        self.pausado = False
        self.data = pd.DataFrame()

        self.setWindowTitle("Monitoreo - Banco de pruebas")
        self.showMaximized()

        self.pila = QStackedLayout()  # Se usa para poder cambiar entre la vista principal y la vista expandida de las gráficas
        self.widget_principal = QWidget() 
        self.layout_principal = QHBoxLayout(self.widget_principal)
        self.pila.addWidget(self.widget_principal)

        widget_central = QWidget()
        widget_central.setLayout(self.pila)
        self.setCentralWidget(widget_central)

        # Layout principal vertical para organizar todo
        layout_principal_v = QVBoxLayout()
        
        # Layout para las gráficas
        layout_graficas = QHBoxLayout()
        self.graficas = {}

        self.mapeo_columnas = {
            "Masa": "masa",
            "Empuje ": "empuje"
        }

        # Crear un contenedor para cada gráfica
        for titulo, columna in self.mapeo_columnas.items():
            contenedor_grafica = QVBoxLayout()
            self.agregar_grafica(contenedor_grafica, titulo)
            layout_graficas.addLayout(contenedor_grafica)

        # Layout para los botones en la parte inferior
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(15)
        
        self.boton_pausar = QPushButton("PAUSAR")
        self.boton_pausar.setCheckable(True)
        self.boton_pausar.clicked.connect(self.alternar_pausa)
        self.boton_pausar.setStyleSheet("background-color: orange; color: black; font-size: 16px; padding: 10px;")
        self.boton_pausar.setFixedWidth(200)

        self.boton_limpiar = QPushButton("LIMPIAR")
        self.boton_limpiar.setStyleSheet("background-color: #A6FF47; font-size: 16px; padding: 10px;")
        self.boton_limpiar.clicked.connect(self.limpiar)
        self.boton_limpiar.setFixedWidth(200)

        # Centrar los botones
        layout_botones.addStretch()
        layout_botones.addWidget(self.boton_pausar)
        layout_botones.addWidget(self.boton_limpiar)
        layout_botones.addStretch()

        # Agregar los layouts al layout principal vertical
        layout_principal_v.addLayout(layout_graficas)
        layout_principal_v.addLayout(layout_botones)
        
        # layout principal
        self.layout_principal.addLayout(layout_principal_v)

        self.setStyleSheet("background-color: #3d3d3d; color: white;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(100)
   
        
  
    
    #Función para agregar gráficas al layout
    def agregar_grafica(self, layout, titulo):
        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setAlignment(Qt.AlignCenter)
        etiqueta_titulo.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        figura = plt.figure(figsize=(6, 4), facecolor="#3d3d3d")
        ax = figura.add_subplot(111)  # Crear el eje aquí, solo una vez

        canvas = FigureCanvas(figura)
        canvas.mousePressEvent = lambda event, t=titulo: self.expandir_grafica(t) # Callback al hacer click en la gráficas

        etiqueta_valor = QLabel("—")
        etiqueta_valor.setAlignment(Qt.AlignCenter)
        etiqueta_valor.setStyleSheet("color: #A6FF47; font-size: 14px;")

        layout.addWidget(etiqueta_titulo)
        layout.addWidget(canvas)
        layout.addWidget(etiqueta_valor)

        self.graficas[titulo] = {
            "figura": figura,
            "canvas": canvas,
            "ax": ax,               # Guardar el eje para reutilizar
            "label": etiqueta_valor
        }

   
   
    def actualizar_datos(self):
        if self.pausado:
            return
        
         # Leer y procesar un solo dato
        dato = self.lector_serial.leer_dato()

        if dato['masa'] is not None and dato['empuje'] is not None:
        # Guardar directamente en la base de datos
            dato['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.db.insertar_dato(dato)
        # Actualizar cada gráfica con su valor correspondiente
            for titulo, columna in self.mapeo_columnas.items():
                self.actualizar_grafica(titulo, dato[columna])
        else:
            return

                

   
    def actualizar_grafica(self, titulo, valor):

        grafica = self.graficas[titulo]
        ax = grafica["ax"]
        canvas = grafica["canvas"]
        etiqueta_valor = grafica["label"]


         # Inicializar el historial si no existe
        if not hasattr(self, 'datos_grafica'):
            self.datos_grafica = {titulo: [] for titulo in self.mapeo_columnas.keys()}
    
        # Agregar el nuevo valor al historial (sin límite: anteiormente había un límite de 100)
        self.datos_grafica[titulo].append(valor)
    
        # Graficar todo el historial
        ax.clear()
        ax.plot(self.datos_grafica[titulo], color='white')
        ax.set_facecolor("#3d3d3d")
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.figure.tight_layout()
        canvas.draw()

        # Actualizar el valor actual
        etiqueta_valor.setText(f"{valor:.2f}")

   
    #Función para expandir la gráfica de un sensor
    # y mostrarla en una vista expandida
    def expandir_grafica(self, titulo):
        columna = self.mapeo_columnas[titulo]

        def obtener_datos():
            # Retornar todos los datos para la vista expandida
            return self.data.index, self.data[columna]

        self.grafica_expandida = GraficaExpandible(titulo, obtener_datos, self.restaurar_vista_principal) #Se crea una instancia de GraficaExpandible (grafica_expandida) y se pasan los parametros correspondientes (titulo -> titulo, obtener_datos -> obtener_datos_calback, restaurar_vista_principal -> regresar_callback)
        self.pila.addWidget(self.grafica_expandida)
        self.pila.setCurrentWidget(self.grafica_expandida)
    
    
    #Función para restaurar la vista principal
    # y ocultar la gráfica expandida
    def restaurar_vista_principal(self):
        self.pila.setCurrentWidget(self.widget_principal)
        self.grafica_expandida = None
    
    
    #Función para alternar entre pausar y reanudar la lectura de datos
    # y cambiar el color del botón de pausa
    def alternar_pausa(self):
        self.pausado = not self.pausado
        self.boton_pausar.setText("REANUDAR" if self.pausado else "PAUSAR")
        color = "green" if self.pausado else "orange"
        self.boton_pausar.setStyleSheet(f"background-color: {color}; color: black; font-size: 16px; padding: 10px;")
    
    
    #Función para reiniciar el buffer de datos
    # y el índice actual
    def limpiar(self):
        if hasattr(self, 'datos_grafica'):  # hasattr se usa para verificar si un objeto(en este caso ventana-principal) tiene un atributo específico (datos_grafica)
            for titulo in self.mapeo_columnas.keys():
                self.datos_grafica[titulo] = []  # Limpia los datos de cada gráfica
            # Redibujar las gráficas vacías
                grafica = self.graficas[titulo] # Accede al diccionario que guarda la info de la gráfica
                ax = grafica["ax"]
                ax.clear()
                ax.set_facecolor("#3d3d3d")
                grafica["canvas"].draw()
                grafica["label"].setText("—")
        self.indice_actual = 0
 
if __name__ == "__main__":
    lector = LectorSerial("COM6", 9600)

    app = QApplication(sys.argv)
    ventana = VentanaPrincipal(lector)

    timer_lectura = QTimer()
    timer_lectura.timeout.connect(lector.leer_dato)
    timer_lectura.start(200)

    ventana.show()
    sys.exit(app.exec_())
