import serial
import time

PUERTO = "/dev/ttyACM0"

print("Abriendo conexión con SPIKE Prime...")

hub = serial.Serial(
    PUERTO,
    baudrate=115200,
    timeout=1
)

time.sleep(1)

print("Conexión abierta.")
print("Esperando datos del Hub...")

for i in range(5):
    datos = hub.read(100)

    if datos:
        print("Datos recibidos:", datos.hex())
    else:
        print("Sin datos.")

    time.sleep(0.5)

hub.close()

print("Conexión cerrada.")