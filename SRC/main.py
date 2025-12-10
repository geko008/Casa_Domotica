# ================================
#      DOMÓTICA ESP32 – MQTT
# DHT11 + MQ2 + 4 Ventiladores + Buzzer
# ================================

import network
import time
import machine
from machine import Pin, ADC
import dht
from umqtt_simple import MQTTClient

# ===== CONFIGURACIÓN WIFI =====
WIFI_SSID = "POCO X6 Pro 5G"
WIFI_PASSWORD = "paulo1234"

# ===== CONFIGURACIÓN MQTT =====
# CAMBIAR ESTA IP POR LA IP DE TU COMPUTADORA CON MOSQUITTO
MQTT_BROKER ="broker.hivemq.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32_domotica"

TOPIC_CMD_FANS   = b"casa/sala/fans/cmd"
TOPIC_CMD_BUZZER = b"casa/sala/buzzer/cmd"
TOPIC_DATA_DHT   = b"casa/sala/dht11"
TOPIC_DATA_GAS   = b"casa/sala/gas"

# ===== PINES =====
PIN_DHT = 4
PIN_MQ2_ADC = 34
PIN_BUZZER = 23

PIN_FAN1 = 16
PIN_FAN2 = 17
PIN_FAN3 = 18
PIN_FAN4 = 19

# ===== OBJETOS =====
#dht11 = dht.DHT11(Pin(PIN_DHT))

mq2 = ADC(Pin(PIN_MQ2_ADC))
mq2.atten(ADC.ATTN_11DB)
mq2.width(ADC.WIDTH_12BIT)

fan1 = Pin(PIN_FAN1, Pin.OUT, value=1)
fan2 = Pin(PIN_FAN2, Pin.OUT, value=1)
fan3 = Pin(PIN_FAN3, Pin.OUT, value=1)
fan4 = Pin(PIN_FAN4, Pin.OUT, value=1)

buzzer = Pin(PIN_BUZZER, Pin.OUT, value=0)

# =============================
#       FUNCIÓN WI-FI
# =============================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)

    # Reinicio preventivo del WiFi (evita Internal State Error)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)

    print("Conectando a WiFi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if not wlan.isconnected():
        raise RuntimeError("No se pudo conectar a WiFi")

    print("Conectado a WiFi:", wlan.ifconfig())


# =============================
#      CONTROL DE ACTUADORES
# =============================
def set_all_fans(on):
    val = 0 if on else 1
    fan1.value(val)
    fan2.value(val)
    fan3.value(val)
    fan4.value(val)

def set_fan(n, on):
    val = 0 if on else 1
    if n == 1: fan1.value(val)
    elif n == 2: fan2.value(val)
    elif n == 3: fan3.value(val)
    elif n == 4: fan4.value(val)


# =============================
#       CALLBACK MQTT
# =============================
def mensaje_mqtt(topic, msg):
    try:
        print("MQTT mensaje:", topic, msg)
        ms = msg.decode().upper()

        if topic == TOPIC_CMD_FANS:
            if ms == "ON":
                set_all_fans(True)
            elif ms == "OFF":
                set_all_fans(False)
            elif ms.startswith("SET:"):
                n = int(ms.split(":")[1])
                set_fan(n, True)

        elif topic == TOPIC_CMD_BUZZER:
            buzzer.value(1 if ms == "ON" else 0)

    except Exception as e:
        print("Error en callback:", e)


# =============================
#       PUBLICAR SENSORES
# =============================
def publicar_dht(cliente):
    try:
        dht11.measure()
        t = dht11.temperature()
        h = dht11.humidity()
        payload = '{"temp": %d, "hum": %d}' % (t, h)
        cliente.publish(TOPIC_DATA_DHT, payload)
    except Exception as e:
        print("Error DHT11:", e)

def publicar_gas(cliente):
    try:
        val = mq2.read()
        payload = '{"adc": %d}' % val
        cliente.publish(TOPIC_DATA_GAS, payload)
    except Exception as e:
        print("Error MQ2:", e)


# =============================
#             MAIN
# =============================
def main():
    conectar_wifi()

    print("Conectando a MQTT...")
    cliente = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    cliente.set_callback(mensaje_mqtt)
    cliente.connect()
    cliente.subscribe(TOPIC_CMD_FANS)
    cliente.subscribe(TOPIC_CMD_BUZZER)

    print("MQTT conectado y suscrito. Sistema iniciado.")

    while True:
        cliente.check_msg()  # recibe mensajes
        publicar_dht(cliente)
        publicar_gas(cliente)
        time.sleep(3)


main()
