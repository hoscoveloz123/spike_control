import spremote
import time

PUERTO = "/dev/ttyACM0"
UMBRAL_NEGRO = 500

print("Conectando al Hub...")

hub = spremote.Hub(PUERTO)
sensor = spremote.ColorSensor(hub, "D")

print("Sensor conectado en D.")
print("Coloca el sensor sobre negro o blanco.")
print("Ctrl+C para terminar.\n")

try:
    while True:
        rojo, verde, azul, intensidad = sensor.get_raw_color()

        if intensidad < UMBRAL_NEGRO:
            estado = "NEGRO"
        else:
            estado = "NO NEGRO"

        print(
            f"R: {rojo:4} | "
            f"G: {verde:4} | "
            f"B: {azul:4} | "
            f"Intensidad: {intensidad:4} | "
            f"Estado: {estado}"
        )

        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nPrueba terminada.")

finally:
    hub.disconnect()