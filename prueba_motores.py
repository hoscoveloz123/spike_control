import spremote
import time

PUERTO = "/dev/ttyACM0"

print("Conectando al Hub...")

hub = spremote.Hub(PUERTO)

print("Hub conectado.")

print("Dispositivos conectados:")
print(hub.list_devices())

print("Creando motores...")

motor_a = spremote.Motor(hub, "A", speed=20)
motor_b = spremote.Motor(hub, "B", speed=20)

print("Motores encontrados.")

print("Motor A girando...")
motor_a.start(speed=20)

time.sleep(2)

print("Deteniendo motor A...")
motor_a.stop()

time.sleep(1)

print("Motor B girando...")
motor_b.start(speed=20)

time.sleep(2)

print("Deteniendo motor B...")
motor_b.stop()

print("Prueba terminada.")

hub.disconnect()