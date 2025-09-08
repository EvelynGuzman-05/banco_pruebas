import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QGridLayout, QStackedLayout, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from db import BaseDatos
from lector_serial import LectorSerial



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
        self.db = BaseDatos()
        self.ultimo_guardado = 0
        self.lector_serial = lector_serial
        self.indice_actual = 0
        self.grafica_expandida = None
        self.pausado = False
        self.data = pd.DataFrame()

        self.setWindowTitle("Monitoreo - Banco de pruebas")
        self.showMaximized()

        self.pila = QStackedLayout()
        self.widget_principal = QWidget()
        self.layout_principal = QHBoxLayout(self.widget_principal)
        self.pila.addWidget(self.widget_principal)

        widget_central = QWidget()
        widget_central.setLayout(self.pila)
        self.setCentralWidget(widget_central)

        layout_izquierdo = QVBoxLayout()
        layout_izquierdo.setSpacing(15)
        layout_izquierdo.setAlignment(Qt.AlignTop)


        self.label_masa = self.crear_etiqueta_sensor("MASA", "0 g\t")
        self.label_empuje = self.crear_etiqueta_sensor("EMPUJE", "0 N")
        
        self.boton_pausar = QPushButton("PAUSAR")
        self.boton_pausar.setCheckable(True)
        self.boton_pausar.clicked.connect(self.alternar_pausa)
        self.boton_pausar.setStyleSheet("background-color: orange; color: black; font-size: 16px; padding: 10px;")

        self.boton_reiniciar = QPushButton("REINICIAR")
        self.boton_reiniciar.setStyleSheet("background-color: #A6FF47; font-size: 16px; padding: 10px;")
        self.boton_reiniciar.clicked.connect(self.reiniciar)

        #layout_izquierdo.addWidget(self.label_tiempo)
        layout_izquierdo.addWidget(self.label_masa)
        layout_izquierdo.addWidget(self.label_empuje)
        #layout_izquierdo.addWidget(self.label_altitud)
        layout_izquierdo.addWidget(self.boton_pausar)
        layout_izquierdo.addWidget(self.boton_reiniciar)

       
        # Checklist para el estado 
        
        #self.estado_diccionario= {
        #    433: "LoRa inicio correctamente",
        #    434: "Error al iniciar el LoRa",
        #    280: "Bmp inicio correctamente",
        #    281: "Error al iniciar el bmp",
        #    100: "Todo el sistema inicio correctamente",
        #    200: "Sistema activado por altitud",
        #    300: "Activación por descenso",
        #    400: "Activación por cambio en la aceleración"
        #}

        #self.checkboxes_estado = {}
        #group_estado = QGroupBox("Estado del sistema")
        #group_estado.setStyleSheet("QGroupBox { color: #A6FF47; font-size: 16px; font-weight: bold; border: 2px solid #A6FF47; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }")
        #vbox_estado = QVBoxLayout()
        #for code, desc in self.estado_diccionario.items():
        #    cb = QCheckBox(desc)
        #    cb.setEnabled(False)
        #    cb.setStyleSheet("color: white; font-size: 14px;")
        #    vbox_estado.addWidget(cb)
        #    self.checkboxes_estado[code] = cb
        #group_estado.setLayout(vbox_estado)
        #layout_izquierdo.addWidget(group_estado)

    
        layout_derecho = QGridLayout()
        self.graficas = {}

        self.mapeo_columnas = {
            "Masa": "masa",
            "Empuje ": "empuje"
        }

        fila_col = [(0,0),(0,1)]
        for (titulo, columna), (fila, col) in zip(self.mapeo_columnas.items(), fila_col):
            self.agregar_grafica(layout_derecho, titulo, fila, col)

        self.layout_principal.addLayout(layout_izquierdo, 2)
        self.layout_principal.addLayout(layout_derecho, 5)

        self.setStyleSheet("background-color: #3d3d3d; color: white;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(100)
   
   
    #Función para crear etiquetas de sensores
    def crear_etiqueta_sensor(self, nombre, valor):
        label = QLabel(f"{nombre}: {valor}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #A6FF47; background-color: #2E2E2E; font-size: 18px; font-weight: bold; padding: 10px; border: 2px solid white;")
        return label
    
    
    #Función para agregar gráficas al layout
    def agregar_grafica(self, layout, titulo, fila, columna):
        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setAlignment(Qt.AlignCenter)
        etiqueta_titulo.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        figura = plt.figure(figsize=(4.5, 3.5), facecolor="#3d3d3d")
        ax = figura.add_subplot(111)  # Crear el eje aquí, solo una vez

        canvas = FigureCanvas(figura)
        canvas.mousePressEvent = lambda event, t=titulo: self.expandir_grafica(t)

        etiqueta_valor = QLabel("—")
        etiqueta_valor.setAlignment(Qt.AlignCenter)
        etiqueta_valor.setStyleSheet("color: #A6FF47; font-size: 14px;")

        layout.addWidget(etiqueta_titulo, fila * 3, columna)
        layout.addWidget(canvas, fila * 3 + 1, columna)
        layout.addWidget(etiqueta_valor, fila * 3 + 2, columna)

        self.graficas[titulo] = {
            "figura": figura,
            "canvas": canvas,
            "ax": ax,               # Guardar el eje para reutilizar
            "label": etiqueta_valor
        }

   
   
    def actualizar_datos(self):
        if self.pausado or not self.lector_serial.buffer_datos:
            return

        self.data = pd.DataFrame(self.lector_serial.buffer_datos)

        if self.data.empty:
            return

    #  Guardar todos los datos nuevos en la base 
        nuevos_datos = self.lector_serial.buffer_datos[self.ultimo_guardado:]
        for fila in nuevos_datos:
            self.db.insertar_dato(fila)
        self.ultimo_guardado += len(nuevos_datos)

        fila = self.data.iloc[-1]  # Usar solo el último para mostrar y graficar

        #def mostrar_valor(valor, sufijo):
        #    if valor is None or pd.isna(valor):
        #        return "—"
        #    return f"{valor:.2f} {sufijo}"

        #self.label_temperatura.setText(f"TEMPERATURA: {mostrar_valor(fila.get('t'), '°C')}")
        #self.label_presion.setText(f"PRESIÓN: {mostrar_valor(fila.get('p'), 'hPa')}")
        #self.label_altitud.setText(f"ALTITUD: {mostrar_valor(fila.get('a'), 'm')}")

    # Actualizar checklist de estado
    #    e = fila.get('e')
    #    for code, cb in self.checkboxes_estado.items():
    #        cb.setChecked(bool(code == e))
    #
        for titulo, columna in self.mapeo_columnas.items():
            self.actualizar_grafica(titulo, columna)

        if self.grafica_expandida:
            self.grafica_expandida.actualizar()

   
   
    def actualizar_grafica(self, titulo, columna):
        if self.data.empty:
            return

        grafica = self.graficas[titulo]
        ax = grafica["ax"]
        canvas = grafica["canvas"]
        etiqueta_valor = grafica["label"]

        x = self.data.index[-100:]
        y = self.data[columna].iloc[-100:]

        if x.empty or y.empty:
            return

        ax.clear()  # Limpiar solo el eje, no toda la figura
        ax.plot(x, y, color='white')
        ax.set_facecolor("#3d3d3d")
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.figure.tight_layout()
        canvas.draw()

        valor = y.iloc[-1]
        etiqueta_valor.setText("—" if pd.isna(valor) else f"{valor:.2f}")

   
   
    #Función para expandir la gráfica de un sensor
    # y mostrarla en una vista expandida
    def expandir_grafica(self, titulo):
        columna = self.mapeo_columnas[titulo]

        def obtener_datos():
            return self.data.index, self.data[columna]

        self.grafica_expandida = GraficaExpandible(titulo, obtener_datos, self.restaurar_vista_principal)
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
    def reiniciar(self):
        self.lector_serial.buffer_datos.clear()
        self.indice_actual = 0
 
if __name__ == "__main__":
    lector = LectorSerial("COM7", 9600)


    app = QApplication(sys.argv)
    ventana = VentanaPrincipal(lector)

    timer_lectura = QTimer()
    timer_lectura.timeout.connect(lector.leer_dato)
    timer_lectura.start(100)

    ventana.show()
    sys.exit(app.exec_())
