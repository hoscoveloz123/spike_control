import serial

PUERTO = "/dev/ttyACM0"
BAUDRATE = 115200

print("Conectando al SPIKE Prime...")

try:
    hub = serial.Serial(
        port=PUERTO,
        baudrate=BAUDRATE,
        timeout=1
    )

    print("Hub conectado correctamente.")
    print(f"Puerto: {PUERTO}")
    print(f"Baudrate: {BAUDRATE}")

    hub.close()

except Exception as e:
    print("Error:", e)