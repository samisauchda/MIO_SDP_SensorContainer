import yaml
import paho.mqtt.client as mqtt
import time
import json
import random


def load_config(config_file):
    """Load configuration from YAML file"""
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def on_connect(client, userdata, flags, rc):
    """Callback for MQTT connection"""
    if rc == 0:
        print("Connected to MQTT Broker successfully!")
    else:
        print(f"Failed to connect, return code {rc}")


def publish_discovery_config(
    client,
    device_name,
    sensor_type,
    unit_of_measurement=None,
    device_class=None,
    unitOfMeasurement=None  # backward compatibility for tests
):
    """
    Publish Home Assistant MQTT Discovery configuration
    Backward compatible with old test calls.
    """

    # Backward compatibility: tests use unitOfMeasurement
    if unit_of_measurement is None and unitOfMeasurement is not None:
        unit_of_measurement = unitOfMeasurement

    device_id = device_name.lower().replace(" ", "_")
    topic = f"homeassistant/sensor/{device_id}_{sensor_type}/config"

    payload = {
        "name": f"{device_name} {sensor_type.capitalize()}",
        "state_topic": f"homeassistant/sensor/{device_id}/{sensor_type}/state",
        "unique_id": f"{device_id}_{sensor_type}",
        "unit_of_measurement": unit_of_measurement,
        "device_class": device_class,
        "device": {
            "identifiers": [device_id],
            "name": device_name,
            "manufacturer": "Custom",
            "model": "Simulated Sensor"
        }
    }

    client.publish(topic, json.dumps(payload), retain=True)
    print(f"Published discovery config for {sensor_type}")


def simulate_sensor_value(min_val, max_val, noise=0.0):
    """Simulate a sensor value with optional noise"""
    base_value = random.uniform(min_val, max_val)
    noisy_value = base_value + random.uniform(-noise, noise)
    return round(noisy_value, 2)


def main():
    print("Loading configuration...")
    config = load_config("SENSOR_SIMULATION/config.yml")

    # MQTT configuration
    mqtt_cfg = config["mqtt"]
    broker = mqtt_cfg["broker"]
    port = mqtt_cfg["port"]
    username = mqtt_cfg["username"]
    password = mqtt_cfg["password"]

    # Device configuration
    device_name = config["device"]["name"]
    device_id = device_name.lower().replace(" ", "_")

    # Sensor configuration (first sensor entry)
    sensor_cfg = config["sensors"][0]
    update_interval = sensor_cfg["update_interval"]

    temp_min = sensor_cfg["temperature_min"]
    temp_max = sensor_cfg["temperature_max"]
    hum_min = sensor_cfg["humidity_min"]
    hum_max = sensor_cfg["humidity_max"]

    temp_noise = sensor_cfg.get("temperature_noise", 0.0)
    hum_noise = sensor_cfg.get("humidity_noise", 0.0)

    # MQTT client setup
    client = mqtt.Client(client_id=f"{device_id}_sensor_container")
    client.username_pw_set(username, password)
    client.on_connect = on_connect

    print(f"Connecting to MQTT broker at {broker}:{port}...")
    client.connect(broker, port, 60)
    client.loop_start()

    time.sleep(2)

    # Home Assistant discovery
    print("Publishing Home Assistant discovery configs...")
    publish_discovery_config(
        client,
        device_name,
        sensor_type="temperature",
        unit_of_measurement="°C",
        device_class="temperature"
    )

    publish_discovery_config(
        client,
        device_name,
        sensor_type="humidity",
        unit_of_measurement="%",
        device_class="humidity"
    )

    print(f"Starting sensor simulation (every {update_interval}s). Press Ctrl+C to stop.")

    try:
        while True:
            temperature = simulate_sensor_value(temp_min, temp_max, temp_noise)
            humidity = simulate_sensor_value(hum_min, hum_max, hum_noise)

            temp_topic = f"homeassistant/sensor/{device_id}/temperature/state"
            hum_topic = f"homeassistant/sensor/{device_id}/humidity/state"

            client.publish(temp_topic, temperature)
            client.publish(hum_topic, humidity)

            print(f"Published temperature={temperature} °C, humidity={humidity} %")
            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("\nStopping sensor simulation...")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected from MQTT broker")


if __name__ == "__main__":
    main()
