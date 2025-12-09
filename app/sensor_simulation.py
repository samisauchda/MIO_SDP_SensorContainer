import time
import json
import random
from datetime import datetime, timezone

import yaml
import paho.mqtt.client as mqtt


# ==========================
# KONFIGURATION AUS config.yml
# ==========================

def load_config(path: str = "config.yml") -> dict:
    """Lädt die Konfiguration aus einer YAML-Datei."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

mqtt_cfg = config.get("mqtt", {})
device_cfg = config.get("device", {})
sensor_cfg = config.get("sensor", {})

MQTT_BROKER = mqtt_cfg.get("broker", "localhost")
MQTT_PORT = mqtt_cfg.get("port", 1883)
MQTT_USERNAME = mqtt_cfg.get("username", "")
MQTT_PASSWORD = mqtt_cfg.get("password", "")
MQTT_TOPIC = mqtt_cfg.get("topic", "office/simulated/sensor1")

SENSOR_ID = device_cfg.get("name", "sim01")

# Intervall in Sekunden
SEND_INTERVAL_SECONDS = sensor_cfg.get("update_interval", 300)

# Simulationsparameter
TEMP_MIN = sensor_cfg.get("temperature_min", 20.0)   # °C
TEMP_MAX = sensor_cfg.get("temperature_max", 28.0)   # °C
HUM_MIN = sensor_cfg.get("humidity_min", 40.0)       # % r.F.
HUM_MAX = sensor_cfg.get("humidity_max", 60.0)       # % r.F.


# ==========================
# HILFSFUNKTIONEN
# ==========================

def generate_simulated_values():
    """Erzeugt simulierte Temperatur- und Feuchtigkeitswerte."""
    temperature = random.uniform(TEMP_MIN, TEMP_MAX)
    humidity = random.uniform(HUM_MIN, HUM_MAX)
    return round(temperature, 2), round(humidity, 2)


def current_timestamp_iso():
    """Gibt aktuellen Zeitpunkt als ISO-String in UTC zurück."""
    return datetime.now(timezone.utc).isoformat()


# ==========================
# MQTT SETUP
# ==========================

client = mqtt.Client(client_id="simulated_sensor_client")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Mit MQTT-Broker verbunden")
    else:
        print(f"Verbindung fehlgeschlagen, rc={rc}")


client.on_connect = on_connect


def connect_mqtt():
    """Stellt die Verbindung zum MQTT-Broker her. Versucht bei Fehlern erneut."""
    # Falls Username gesetzt → Auth aktivieren
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    while True:
        try:
            print(f"Verbinde mit MQTT-Broker {MQTT_BROKER}:{MQTT_PORT} ...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_start()
            break
        except Exception as e:
            print(f"Fehler bei MQTT-Verbindung: {e}")
            print("Neuer Versuch in 5 Sekunden ...")
            time.sleep(5)


# ==========================
# HAUPTSCHLEIFE
# ==========================

def main():
    connect_mqtt()

    print("Starte Sensorsimulation...")
    print(f"Sensor-ID: {SENSOR_ID}")
    print(f"Intervall: alle {SEND_INTERVAL_SECONDS} Sekunden")
    print(f"MQTT Topic: {MQTT_TOPIC}")
    print("------------------------------")

    try:
        while True:
            # 1) Werte simulieren
            temperature, humidity = generate_simulated_values()
            timestamp = current_timestamp_iso()

            # 2) JSON-Payload bauen
            payload = {
                "sensor_id": SENSOR_ID,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": timestamp,
            }

            payload_str = json.dumps(payload)

            # 3) Log-Ausgabe
            print(f"Sende: {payload_str}")

            # 4) MQTT Publish
            try:
                result = client.publish(MQTT_TOPIC, payload_str, qos=0)
                status = result[0]
                if status == 0:
                    print("MQTT Publish OK")
                else:
                    print(f"MQTT Publish fehlgeschlagen, Status: {status}")
            except Exception as e:
                print(f"Fehler beim Senden: {e}")

            # 5) Warten bis zur nächsten Messung
            time.sleep(SEND_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulation manuell beendet (Ctrl+C).")
    finally:
        client.loop_stop()
        client.disconnect()
        print("MQTT-Verbindung geschlossen.")


if __name__ == "__main__":
    main()
