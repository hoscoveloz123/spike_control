import tkinter as tk
import spremote

# ============================================================
# CONFIGURACIÓN DE PUERTOS
# ============================================================

PUERTO = "/dev/ttyACM0"

# Motores
PUERTO_IZQUIERDA = "B"
PUERTO_DERECHA = "F"
PUERTO_CATAPULTA = "E"

# Sensores
PUERTO_SENSOR_DISTANCIA = "D"
PUERTO_SENSOR_COLOR = "C"

# ============================================================
# CONFIGURACIÓN DEL DISPARO AUTOMÁTICO Y UMBRAL DE COLOR
# ============================================================

DISTANCIA_OBJETIVO = 63.5       # cm
TOLERANCIA = 1.0                # ±1 cm

POTENCIA_AUTOMATICA = 70        # %
TIEMPO_DISPARO = 4              # segundos

UMBRAL_NEGRO = 10               # Si los valores son menores a este número, se considera NEGRO

# ============================================================
# VARIABLES
# ============================================================

automatico_activo = False
disparando = False
objetivo_detectado = False

desea_avanzar = False           
es_color_negro = False
texto_color_mostrar = "Ninguno"

# ============================================================
# CONEXIÓN CON EL HUB
# ============================================================

try:
    hub = spremote.Hub(PUERTO)

    motor_izq = spremote.Motor(hub, PUERTO_IZQUIERDA, lock=False)
    motor_der = spremote.Motor(hub, PUERTO_DERECHA, lock=False)
    motor_catapulta = spremote.Motor(hub, PUERTO_CATAPULTA, lock=False)

    sensor_distancia = spremote.DistanceSensor(hub, PUERTO_SENSOR_DISTANCIA)

    try:
        sensor_color = spremote.ColorSensor(hub, PUERTO_SENSOR_COLOR)
        color_conectado = True
    except Exception as e_col:
        print(f"⚠️ Aviso: No se pudo conectar el sensor de color en puerto {PUERTO_SENSOR_COLOR}:", e_col)
        sensor_color = None
        color_conectado = False

    conexion_correcta = True
    print("✅ Conexión con el Hub establecida con éxito en /dev/ttyACM0")

except Exception as e:
    conexion_correcta = False
    color_conectado = False
    print("❌ ERROR AL CONECTAR CON EL HUB:", e)

# ============================================================
# VENTANA
# ============================================================

ventana = tk.Tk()
ventana.title("Control LEGO SPIKE Prime")
ventana.geometry("800x920")
ventana.resizable(True, True)

# ============================================================
# VARIABLES DE LA INTERFAZ
# ============================================================

potencia_ruedas = tk.IntVar(value=50)
potencia_catapulta = tk.IntVar(value=70)

# ============================================================
# FUNCIONES DE MOVIMIENTO
# ============================================================

def detener_robot():
    global desea_avanzar
    desea_avanzar = False
    if not conexion_correcta:
        return
    try:
        motor_izq.stop()
        motor_der.stop()
        etiqueta_movimiento.config(text="🛑 Robot detenido")
    except Exception as e:
        print("Error deteniendo robot:", e)

def adelante():
    global desea_avanzar
    if not conexion_correcta:
        return

    desea_avanzar = True

    # REGLA: AVANZAR SOLO SI NO ES NEGRO
    if not es_color_negro:
        potencia = potencia_ruedas.get()
        try:
            motor_izq.start(potencia)
            motor_der.start(-potencia)
            etiqueta_movimiento.config(text="⬆️ Avanzando (Color 'NEGRO' detectado)")
        except Exception as e:
            print("Error al avanzar:", e)
    else:
        detener_robot()
        etiqueta_movimiento.config(text=f"🛑 Bloqueado: Color NO NEGRO detectado ({texto_color_mostrar})")

def atras():
    global desea_avanzar
    desea_avanzar = False
    if not conexion_correcta:
        return
    potencia = potencia_ruedas.get()
    try:
        motor_izq.start(-potencia)
        motor_der.start(potencia)
        etiqueta_movimiento.config(text="⬇️ Retrocediendo")
    except Exception as e:
        print("Error al retroceder:", e)

def izquierda():
    global desea_avanzar
    desea_avanzar = False
    if not conexion_correcta:
        return
    potencia = potencia_ruedas.get()
    try:
        motor_izq.start(-potencia)
        motor_der.start(-potencia)
        etiqueta_movimiento.config(text="⬅️ Girando izquierda")
    except Exception as e:
        print("Error al girar izquierda:", e)

def derecha():
    global desea_avanzar
    desea_avanzar = False
    if not conexion_correcta:
        return
    potencia = potencia_ruedas.get()
    try:
        motor_izq.start(potencia)
        motor_der.start(potencia)
        etiqueta_movimiento.config(text="➡️ Girando derecha")
    except Exception as e:
        print("Error al girar derecha:", e)

def actualizar_potencia_ruedas(valor):
    etiqueta_potencia_ruedas.config(text=f"{int(float(valor))}%")

# ============================================================
# FUNCIONES MANUALES DE CATAPULTA
# ============================================================

def catapulta_arriba():
    if not conexion_correcta or disparando:
        return
    try:
        motor_catapulta.start(potencia_catapulta.get())
        etiqueta_estado_catapulta.config(text="⬆️ Catapulta subiendo")
    except Exception as e:
        print("Error catapulta:", e)

def catapulta_abajo():
    if not conexion_correcta or disparando:
        return
    try:
        motor_catapulta.start(-potencia_catapulta.get())
        etiqueta_estado_catapulta.config(text="⬇️ Catapulta bajando")
    except Exception as e:
        print("Error catapulta:", e)

def detener_catapulta():
    if not conexion_correcta:
        return
    try:
        motor_catapulta.stop()
        etiqueta_estado_catapulta.config(text="🛑 Catapulta detenida")
    except Exception as e:
        print("Error deteniendo catapulta:", e)

def actualizar_potencia_catapulta(valor):
    etiqueta_potencia_catapulta.config(text=f"{int(float(valor))}%")

# ============================================================
# MODOS Y DISPARO AUTOMÁTICO
# ============================================================

def activar_manual():
    global automatico_activo, disparando, objetivo_detectado
    automatico_activo = False
    objetivo_detectado = False
    if disparando:
        try:
            motor_catapulta.stop()
        except Exception:
            pass
    disparando = False
    etiqueta_modo.config(text="🕹️ MODO MANUAL")
    etiqueta_estado.config(text="Control manual activado")
    etiqueta_estado_catapulta.config(text="Lista para control manual")

def activar_automatico():
    global automatico_activo, objetivo_detectado
    automatico_activo = True
    objetivo_detectado = False
    etiqueta_modo.config(text="🤖 MODO AUTOMÁTICO")
    etiqueta_estado.config(text="Esperando objetivo...")
    etiqueta_estado_catapulta.config(text=f"Objetivo: {DISTANCIA_OBJETIVO} cm")

def disparar_automatico():
    global disparando
    if not conexion_correcta or disparando:
        return
    disparando = True
    etiqueta_estado.config(text="🚀 DISPARANDO...")
    etiqueta_estado_catapulta.config(text="Motor E: 70% durante 4 segundos")
    try:
        motor_catapulta.start(POTENCIA_AUTOMATICA)
        ventana.after(TIEMPO_DISPARO * 1000, terminar_disparo)
    except Exception as e:
        print("Error durante el disparo:", e)
        disparando = False

def terminar_disparo():
    global disparando
    try:
        motor_catapulta.stop()
    except Exception as e:
        print("Error deteniendo catapulta:", e)
    disparando = False
    etiqueta_estado.config(text="🛑 Disparo terminado")
    etiqueta_estado_catapulta.config(text="Esperando nuevo objetivo...")

# ============================================================
# LECTURA DE SENSORES EN TIEMPO REAL
# ============================================================

def actualizar_sensores():
    global objetivo_detectado, es_color_negro, texto_color_mostrar, desea_avanzar

    if not conexion_correcta:
        etiqueta_distancia.config(text="Sin conexión")
        etiqueta_color.config(text="Sin conexión")
        ventana.after(500, actualizar_sensores)
        return

    # --- 1. LECTURA DE DISTANCIA ---
    try:
        distancia_mm = sensor_distancia.get_distance()

        if distancia_mm is not None:
            distancia_cm = distancia_mm / 10.0
            etiqueta_distancia.config(text=f"{distancia_cm:.1f} cm")

            # MODO AUTOMÁTICO
            if automatico_activo and not disparando:
                distancia_min = DISTANCIA_OBJETIVO - TOLERANCIA
                distancia_max = DISTANCIA_OBJETIVO + TOLERANCIA

                if distancia_min <= distancia_cm <= distancia_max:
                    if not objetivo_detectado:
                        objetivo_detectado = True
                        etiqueta_estado.config(text="🎯 OBJETIVO DETECTADO")
                        disparar_automatico()
                else:
                    objetivo_detectado = False
                    if not disparando:
                        etiqueta_estado.config(text="Esperando objetivo...")
        else:
            etiqueta_distancia.config(text="Fuera de rango")

    except Exception as e:
        etiqueta_distancia.config(text="Error lectura")

    # --- 2. LECTURA DE COLOR Y EVALUACIÓN DE NEGRO ---
    if sensor_color is not None:
        try:
            val = None
            if hasattr(sensor_color, 'get_color'):
                val = sensor_color.get_color()
            elif hasattr(sensor_color, 'get_color_name'):
                val = sensor_color.get_color_name()
            elif hasattr(sensor_color, 'color'):
                val = sensor_color.color()

            if val is not None:
                texto_color_mostrar = str(val)

                if isinstance(val, (tuple, list)) and len(val) > 0:
                    primer_valor = val[0]
                    es_color_negro = (primer_valor <= UMBRAL_NEGRO)
                elif isinstance(val, (int, float)):
                    es_color_negro = (val <= UMBRAL_NEGRO)
                else:
                    es_color_negro = any(n in str(val).lower() for n in ["black", "negro", "0"])

                if es_color_negro:
                    etiqueta_color.config(text=f"Color detectado: NEGRO ({texto_color_mostrar})", fg="red")
                else:
                    etiqueta_color.config(text=f"Color detectado: NO NEGRO ({texto_color_mostrar})", fg="green")
            else:
                es_color_negro = False
                texto_color_mostrar = "Sin datos"
                etiqueta_color.config(text="Color: Ninguno / Sin detectar", fg="black")

        except Exception as e:
            es_color_negro = False
            etiqueta_color.config(text="Error leyendo sensor", fg="red")
    else:
        etiqueta_color.config(text=f"⚠️ Sin sensor en Puerto '{PUERTO_SENSOR_COLOR}'", fg="black")

    # --- CONTROL DE AVANCE EN TIEMPO REAL ---
    if desea_avanzar:
        if not es_color_negro:
            # Continúa avanzando si NO es negro
            potencia = potencia_ruedas.get()
            motor_izq.start(potencia)
            motor_der.start(-potencia)
            etiqueta_movimiento.config(text="⬆️ Avanzando (Permitido: 'NO NEGRO')")
        else:
            # Frena inmediatamente al detectar NEGRO
            motor_izq.stop()
            motor_der.stop()
            etiqueta_movimiento.config(text=f"🛑 Detenido: Línea NEGRA detectada ({texto_color_mostrar})")

    ventana.after(150, actualizar_sensores)

# ============================================================
# INTERFAZ GRÁFICA (GUI)
# ============================================================

titulo = tk.Label(ventana, text="🤖 LEGO SPIKE PRIME", font=("Arial", 24, "bold"))
titulo.pack(pady=10)

etiqueta_modo = tk.Label(ventana, text="🕹️ MODO MANUAL", font=("Arial", 16, "bold"))
etiqueta_modo.pack(pady=2)

etiqueta_estado = tk.Label(ventana, text="Listo", font=("Arial", 12))
etiqueta_estado.pack(pady=2)

# SENSORES
marco_sensor = tk.LabelFrame(ventana, text="📊 SENSORES EN TIEMPO REAL", font=("Arial", 12, "bold"), padx=15, pady=5)
marco_sensor.pack(fill="x", padx=20, pady=5)

etiqueta_distancia = tk.Label(marco_sensor, text="---", font=("Arial", 24, "bold"))
etiqueta_distancia.pack()

etiqueta_color = tk.Label(marco_sensor, text="Color: Detectando...", font=("Arial", 12, "bold"))
etiqueta_color.pack(pady=2)

etiqueta_objetivo = tk.Label(marco_sensor, text="Objetivo automático: 63,5 cm ± 1 cm", font=("Arial", 10))
etiqueta_objetivo.pack()

# MODO
marco_modo = tk.LabelFrame(ventana, text="⚙️ MODO DE CONTROL", font=("Arial", 12, "bold"), padx=10, pady=5)
marco_modo.pack(fill="x", padx=20, pady=5)

boton_manual = tk.Button(marco_modo, text="🕹️ MODO MANUAL", font=("Arial", 11, "bold"), width=18, command=activar_manual)
boton_manual.pack(side="left", padx=10, pady=5)

boton_automatico = tk.Button(marco_modo, text="🤖 MODO AUTOMÁTICO", font=("Arial", 11, "bold"), width=18, command=activar_automatico)
boton_automatico.pack(side="right", padx=10, pady=5)

# MOVIMIENTO
marco_movimiento = tk.LabelFrame(ventana, text="🚗 MOVIMIENTO", font=("Arial", 12, "bold"), padx=10, pady=5)
marco_movimiento.pack(padx=20, pady=5)

tk.Label(marco_movimiento, text="Potencia ruedas:", font=("Arial", 10)).grid(row=0, column=0, columnspan=3)
slider_ruedas = tk.Scale(marco_movimiento, from_=0, to=100, orient="horizontal", length=250, variable=potencia_ruedas, command=actualizar_potencia_ruedas)
slider_ruedas.grid(row=1, column=0, columnspan=3)

etiqueta_potencia_ruedas = tk.Label(marco_movimiento, text="50%", font=("Arial", 10, "bold"))
etiqueta_potencia_ruedas.grid(row=2, column=0, columnspan=3)

tk.Button(marco_movimiento, text="⬆️", font=("Arial", 14, "bold"), width=5, command=adelante).grid(row=3, column=1, padx=2, pady=2)
tk.Button(marco_movimiento, text="⬅️", font=("Arial", 14, "bold"), width=5, command=izquierda).grid(row=4, column=0, padx=2, pady=2)
tk.Button(marco_movimiento, text="🛑", font=("Arial", 14, "bold"), width=5, command=detener_robot).grid(row=4, column=1, padx=2, pady=2)
tk.Button(marco_movimiento, text="➡️", font=("Arial", 14, "bold"), width=5, command=derecha).grid(row=4, column=2, padx=2, pady=2)
tk.Button(marco_movimiento, text="⬇️", font=("Arial", 14, "bold"), width=5, command=atras).grid(row=5, column=1, padx=2, pady=2)

etiqueta_movimiento = tk.Label(marco_movimiento, text="🛑 Robot detenido", font=("Arial", 10))
etiqueta_movimiento.grid(row=6, column=0, columnspan=3, pady=2)

# CATAPULTA
marco_catapulta = tk.LabelFrame(ventana, text="🚀 CATAPULTA - MOTOR E", font=("Arial", 12, "bold"), padx=10, pady=5)
marco_catapulta.pack(fill="x", padx=20, pady=5)

slider_catapulta = tk.Scale(marco_catapulta, from_=0, to=100, orient="horizontal", length=250, variable=potencia_catapulta, command=actualizar_potencia_catapulta)
slider_catapulta.pack()

etiqueta_potencia_catapulta = tk.Label(marco_catapulta, text="70%", font=("Arial", 10, "bold"))
etiqueta_potencia_catapulta.pack()

marco_botones_catapulta = tk.Frame(marco_catapulta)
marco_botones_catapulta.pack(pady=5)

tk.Button(marco_botones_catapulta, text="⬆️ SUBIR", font=("Arial", 10, "bold"), width=10, command=catapulta_arriba).pack(side="left", padx=3)
tk.Button(marco_botones_catapulta, text="🛑 STOP", font=("Arial", 10, "bold"), width=10, command=detener_catapulta).pack(side="left", padx=3)
tk.Button(marco_botones_catapulta, text="⬇️ BAJAR", font=("Arial", 10, "bold"), width=10, command=catapulta_abajo).pack(side="left", padx=3)

etiqueta_estado_catapulta = tk.Label(marco_catapulta, text="Lista para control manual", font=("Arial", 10))
etiqueta_estado_catapulta.pack(pady=2)

# CERRAR PROGRAMA
def cerrar_programa():
    global automatico_activo, disparando
    automatico_activo = False
    disparando = False
    if conexion_correcta:
        try:
            motor_izq.stop()
            motor_der.stop()
            motor_catapulta.stop()
            hub.disconnect()
        except Exception as e:
            print("Error al cerrar conexión:", e)
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar_programa)

# Iniciar procesos
actualizar_sensores()
ventana.mainloop()
