import sys
import numpy as np
import ctypes
import time
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox
from PyQt6.QtCore import QTimer
from pyqtgraph import PlotWidget, mkPen
from PyDAQmx import Task, DAQmx_Val_Diff, DAQmx_Val_ContSamps, DAQmx_Val_Rising, DAQmx_Val_GroupByChannel, DAQmx_Val_Volts

# --- Parámetros ---
FS = 250
BUFFER_SIZE = 100
CANAL = "Dev3/ai0"
Y_FIXED_RANGE = (0.08, 0.17)
CSV_FILENAME = "emg_data.csv"

class EMGTask(Task):
    def __init__(self):
        super().__init__()
        self.CreateAIVoltageChan(CANAL, "", DAQmx_Val_Diff, -10.0, 10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("", FS, DAQmx_Val_Rising, DAQmx_Val_ContSamps, BUFFER_SIZE)
        self.StartTask()

    def read(self):
        data = np.zeros(BUFFER_SIZE, dtype=np.float64)
        read = ctypes.c_int32()
        self.ReadAnalogF64(BUFFER_SIZE, 10.0, DAQmx_Val_GroupByChannel, data, BUFFER_SIZE, ctypes.byref(read), None)
        return data if read.value == BUFFER_SIZE else np.zeros(BUFFER_SIZE)

class EMGViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG Viewer - Estilo NI Test Panel")
        self.resize(800, 500)

        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot = self.plot_widget.plot([], pen=mkPen(color='g', width=1))
        self.plot_widget.setLabel("left", "Amplitud (V)")
        self.plot_widget.setLabel("bottom", "Segundos")

        self.auto_scale_checkbox = QCheckBox("Auto-escala")
        self.auto_scale_checkbox.setChecked(True)
        self.auto_scale_checkbox.stateChanged.connect(self.toggle_auto_scale)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.auto_scale_checkbox)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.data = np.zeros(1000)
        self.task = EMGTask()

        # Crear o abrir archivo CSV y escribir encabezado
        self.csv_file = open(CSV_FILENAME, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["timestamp"] + [f"sample_{i}" for i in range(BUFFER_SIZE)])

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)

    def update_plot(self):
        new_data = self.task.read()
        self.data = np.roll(self.data, -len(new_data))
        self.data[-len(new_data):] = new_data
        self.plot.setData(self.data)

        if not self.auto_scale_checkbox.isChecked():
            self.plot_widget.setYRange(*Y_FIXED_RANGE)
        else:
            self.plot_widget.enableAutoRange()

        # Guardar datos con marca de tiempo
        timestamp = time.time()
        self.csv_writer.writerow([timestamp] + list(new_data))

    def toggle_auto_scale(self):
        if self.auto_scale_checkbox.isChecked():
            self.plot_widget.enableAutoRange()
        else:
            self.plot_widget.setYRange(*Y_FIXED_RANGE)

    def closeEvent(self, event):
        self.timer.stop()
        self.task.StopTask()
        self.task.ClearTask()
        self.csv_file.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = EMGViewer()
    viewer.show()
    sys.exit(app.exec())

