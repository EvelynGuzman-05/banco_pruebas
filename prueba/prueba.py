import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,QWidget, QGridLayout, QStackedLayout, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ExpandableGraph(QWidget):
    def __init__(self, title, get_data_callback, back_callback):
        super().__init__()
        self.get_data_callback = get_data_callback

        layout = QVBoxLayout()
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        layout.addWidget(title_label)

        self.figure = plt.figure(facecolor="#3d3d3d")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()


        self.back_btn = QPushButton("← REGRESAR")
        self.back_btn.setStyleSheet("background-color: #A6FF47; font-size: 16px; padding: 10px;")
        self.back_btn.clicked.connect(back_callback)

        button_layout.addWidget(self.back_btn)

        layout.addLayout(button_layout)

    def update_graph(self):
        x, y = self.get_data_callback()
        if len(x) == 0:
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y, color='white')
        ax.set_facecolor("#3d3d3d")
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        self.figure.tight_layout()
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.current_index = 0
        self.expanded_graph_widget = None
        self.paused = False

        self.setWindowTitle("Monitoreo - Estación Terrena")
        self.showFullScreen()

        self.stack = QStackedLayout()
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.stack.addWidget(self.main_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.stack)
        self.setCentralWidget(central_widget)

        # Lado izquierdo
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignTop)

        pos_layout = QHBoxLayout()
        self.orientation_label = self.create_box_label("ORIENTACIÓN")
        self.location_label = self.create_box_label("UBICACIÓN")
        pos_layout.addWidget(self.orientation_label)
        pos_layout.addWidget(self.location_label)

        self.label_tiempo = self.create_sensor_label("TIEMPO", "0 seg")
        self.label_co2 = self.create_sensor_label("CO2", "0 ppm")
        self.label_altura = self.create_sensor_label("ALTURA", "0 m")

        self.btn_detener = QPushButton("PAUSAR")
        self.btn_detener.setCheckable(True)
        self.btn_detener.clicked.connect(self.toggle_update)
        self.btn_detener.setStyleSheet("background-color: orange; color: black; font-size: 16px; padding: 10px;")

        self.btn_reiniciar = QPushButton("REINICIAR")
        self.btn_reiniciar.setStyleSheet("background-color: #A6FF47; font-size: 16px; padding: 10px;")
        self.btn_reiniciar.clicked.connect(self.restart)

        left_layout.addLayout(pos_layout)
        left_layout.addWidget(self.label_tiempo)
        left_layout.addWidget(self.label_co2)
        left_layout.addWidget(self.label_altura)
        left_layout.addWidget(self.btn_detener)
        left_layout.addWidget(self.btn_reiniciar)

        # Lado derecho (gráficas)
        right_layout = QGridLayout()
        self.graphs = {}

        self.add_graph(right_layout, "ALTURA", 0, 0)
        self.add_graph(right_layout, "ACELERACIÓN", 1, 0)
        self.add_graph(right_layout, "VELOCIDAD", 0, 1)
        self.add_graph(right_layout, "TEMPERATURA", 1, 1)

        self.main_layout.addLayout(left_layout, 2)
        self.main_layout.addLayout(right_layout, 5)

        self.setStyleSheet("background-color: #3d3d3d;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def create_box_label(self, text):
        label = QLabel(text)
        label.setFixedSize(200, 200)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background-color: #2E2E2E; color: white; border: 2px solid white;")
        return label

    def create_sensor_label(self, name, value):
        label = QLabel(f"{name}: {value}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #A6FF47; background-color: #2E2E2E; font-size: 18px; font-weight: bold; padding: 10px; border: 2px solid white;")
        return label

    def add_graph(self, layout, title, row, col):
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        fig = plt.figure(figsize=(4.5, 3.5), facecolor="#3d3d3d")
        canvas = FigureCanvas(fig)
        canvas.mousePressEvent = lambda event, t=title: self.expand_graph(t)

        value_label = QLabel("—")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #A6FF47; font-size: 14px;")

        layout.addWidget(title_label, row * 3, col)
        layout.addWidget(canvas, row * 3 + 1, col)
        layout.addWidget(value_label, row * 3 + 2, col)

        self.graphs[title] = {
            "figure": fig,
            "canvas": canvas,
            "label": value_label
        }

    def update_data(self):
        if self.paused:
            return

        if self.current_index < len(self.data):
            row = self.data.iloc[self.current_index]
            self.label_tiempo.setText(f"TIEMPO: {row['Hora']}")
            self.label_co2.setText(f"CO2: {row['CO2']} ppm")
            self.label_altura.setText(f"ALTURA: {row['Altura']} m")

            self.update_graph("ALTURA", "Altura")
            self.update_graph("ACELERACIÓN", "Acel Z")
            self.update_graph("VELOCIDAD", "Giro X")
            self.update_graph("TEMPERATURA", "Temperatura")

            if self.expanded_graph_widget:
                self.expanded_graph_widget.update_graph()

            self.current_index += 1

    def update_graph(self, title, column):
        graph = self.graphs[title]
        fig = graph["figure"]
        canvas = graph["canvas"]
        label = graph["label"]

        x = self.data['Hora'][:self.current_index+1]
        y = self.data[column][:self.current_index+1]
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(x, y, color='white')
        ax.set_facecolor("#3d3d3d")
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        fig.tight_layout()
        canvas.draw()

        
        if not y.empty:
            label.setText(f"{y.iloc[-1]:.2f}")

    def expand_graph(self, title):
        column_map = {
            "ALTURA": "Altura",
            "ACELERACIÓN": "Acel Z",
            "VELOCIDAD": "Giro X",
            "TEMPERATURA": "Temperatura"
        }

        col_name = column_map[title]

        def get_data():
            return self.data['Hora'][:self.current_index+1], self.data[col_name][:self.current_index+1]

        self.expanded_graph_widget = ExpandableGraph(title, get_data, self.restore_main_view)
        self.stack.addWidget(self.expanded_graph_widget)
        self.stack.setCurrentWidget(self.expanded_graph_widget)

    def restore_main_view(self):
        self.stack.setCurrentWidget(self.main_widget)
        self.expanded_graph_widget = None

    def toggle_update(self):
        self.paused = not self.paused
        self.btn_detener.setText("REANUDAR" if self.paused else "PAUSAR")
        color = "green" if self.paused else "orange"
        self.btn_detener.setStyleSheet(f"background-color: {color}; font-size: 16px; padding: 10px;")

    def restart(self):
        self.current_index = 0


if __name__ == "__main__":
    file = 'C:/Users/eveli/Downloads/tiempo_real/prueba_02.csv'
    data = pd.read_csv(file)

    app = QApplication(sys.argv)
    window = MainWindow(data)
    window.show()
    sys.exit(app.exec_())
