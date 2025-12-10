import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC_CMD_FANS   = "casa/sala/fans/cmd"
TOPIC_CMD_BUZZER = "casa/sala/buzzer/cmd"
TOPIC_DATA_DHT   = "casa/sala/dht11"
TOPIC_DATA_GAS   = "casa/sala/gas"

# ============================================================
#             CALLBACKS MQTT
# ============================================================
def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código:", rc)

    # Suscribirse a los tópicos que publica la ESP32
    client.subscribe(TOPIC_DATA_DHT)
    client.subscribe(TOPIC_DATA_GAS)

    # También escucharemos los comandos (por si alguien más los manda)
    client.subscribe(TOPIC_CMD_FANS)
    client.subscribe(TOPIC_CMD_BUZZER)

    print("\nSuscrito a:")
    print(" -", TOPIC_DATA_DHT)
    print(" -", TOPIC_DATA_GAS)
    print(" -", TOPIC_CMD_FANS)
    print(" -", TOPIC_CMD_BUZZER)
    print("===========================================\n")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode()}")


# ============================================================
#     ENVIAR COMANDOS A LA ESP32 DESDE PYTHON
# ============================================================
def enviar_comandos(client):
    print("\nCOMANDOS DISPONIBLES:")
    print("1 → Encender ventiladores")
    print("2 → Apagar ventiladores")
    print("3 → Encender buzzer")
    print("4 → Apagar buzzer")
    print("5 → Ventilador individual (set N)")
    print("0 → Salir\n")

    while True:
        opcion = input("Comando: ")

        if opcion == "1":
            client.publish(TOPIC_CMD_FANS, "ON")
        elif opcion == "2":
            client.publish(TOPIC_CMD_FANS, "OFF")
        elif opcion == "3":
            client.publish(TOPIC_CMD_BUZZER, "ON")
        elif opcion == "4":
            client.publish(TOPIC_CMD_BUZZER, "OFF")
        elif opcion == "5":
            n = input("Número de ventilador (1-4): ")
            client.publish(TOPIC_CMD_FANS, f"SET:{n}")
        elif opcion == "0":
            break
        else:
            print("Opción inválida")


# ============================================================
#                  MAIN
# ============================================================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Conectando al broker...")

client.connect(BROKER, PORT, 60)

client.loop_start()   # permite recibir mensajes en segundo plano

enviar_comandos(client)

client.loop_stop()
client.disconnect()
