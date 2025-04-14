import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# Cargar datos
file_path = r"C:\Users\Esteban\Downloads\senal_emg_ajustada.xlsx"
df = pd.read_excel(file_path)
t = df.iloc[:, 0].values
emg_signal_raw = df.iloc[:, 1].values
fs = 2000  # Frecuencia de muestreo

# ---------------------------------------------------------------
# 2. Ajuste interactivo de parámetros (basado en tu espectro)
# ---------------------------------------------------------------
# MODIFICA ESTOS VALORES SEGÚN LO OBSERVADO EN EL ESPECTRO:
new_w_lower = 20  # Ejemplo: si hay energía relevante <20 Hz
new_w_upper = 440  # Ejemplo: si la señal decae antes de 500 Hz
new_order = 100  # Orden reducido para evitar sobre-atenuación
window_type = 'hamming'

# ---------------------------------------------------------------
# 3. Diseño del filtro ajustado
# ---------------------------------------------------------------
nyq = 0.5 * fs
w1 = new_w_lower / nyq
w2 = new_w_upper / nyq

# Diseñar filtro FIR pasa-banda
filt_coeff = signal.firwin(new_order, [w1, w2], pass_zero=False, window=window_type)

# Aplicar filtro con fase cero (elimina retardo)
filtered_signal = signal.filtfilt(filt_coeff, 1.0, emg_signal_raw)

# ---------------------------------------------------------------
# 4. Visualización comparativa
# ---------------------------------------------------------------
plt.figure(figsize=(15, 6))

# Señal original
plt.subplot(2, 2, 1)
plt.plot(t, emg_signal_raw, color='forestgreen', alpha=0.6, label='Original')
plt.title('Comparación de señales')
plt.ylabel('Voltaje (mV)')
plt.legend()
plt.grid(True)

# Señal filtrada
plt.subplot(2, 2, 3)
plt.plot(t, filtered_signal, color='darkorange', linewidth=1.2, label='Filtrada')
plt.xlabel('Tiempo (s)')
plt.ylabel('Voltaje (mV)')
plt.legend()
plt.grid(True)

# ---------------------------------------------------------------
# 5. Densidad espectral de potencia (PSD) de la señal filtrada
# ---------------------------------------------------------------
f, psd = signal.welch(filtered_signal, fs, nperseg=1024)  # Welch para PSD

plt.subplot(2, 2, 2)
plt.semilogy(f, psd, color='royalblue')  # Escala logarítmica para PSD
plt.title('Densidad Espectral de Potencia (PSD) - Señal Filtrada')
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('PSD [V**2/Hz]')
plt.grid(True)

plt.tight_layout()
plt.show()