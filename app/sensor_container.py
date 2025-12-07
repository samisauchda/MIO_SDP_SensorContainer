import yaml
import paho.mqtt.client as mqtt
import time
import json

def load_config(config_file='config.yml'):
    """Load configuration from YAML file"""
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print("Connected to MQTT Broker successfully!")
    else:
        print(f"Failed to connect, return code {rc}")

def publish_discovery_config(client, device_name, sensor_type, unitOfMeasurement=None, device_class=None):
    """
    Publish Home Assistant MQTT Discovery configuration
    This allows Home Assistant to auto-discover the sensor
    """
    device_id = device_name.lower().replace(' ', '_')
    
    # Discovery topic
    topic = f"homeassistant/sensor/{device_id}_{sensor_type}/config"
    
    # Configuration payload
    config_payload = {
        "name": f"{device_name} {sensor_type.capitalize()}",
        "state_topic": f"homeassistant/sensor/{device_id}/{sensor_type}/state",
        "unique_id": f"{device_id}_{sensor_type}",
        "device": {
            "identifiers": [device_id],
            "name": device_name,
            "model": f"{sensor_type} Sensor",
            "manufacturer": "Custom",
            "unit_of_measurement": unitOfMeasurement,
            "device_class": device_class
        }
    }
    
    # Publish discovery config
    result = client.publish(topic, json.dumps(config_payload), retain=True)
    
    if result[0] == 0:
        print(f"Published discovery config for {sensor_type}")
    else:
        print(f"Failed to publish discovery config for {sensor_type}")


def main():
    """Main function"""
    # Load configuration
    print("Loading configuration from config.yml...")
    config = load_config('config.yml')
    
    # set up mQTT client
    broker = config['mqtt']['broker']
    port = config['mqtt']['port']
    username = config['mqtt']['username']
    password = config['mqtt']['password']
    device_name = config['device']['name']
    sensor_type = config['sensors'][0]['type']  # assuming first sensor for simplicity


    client = mqtt.Client(client_id=f"{device_name}_sensor_container")
    client.username_pw_set(username, password)
    client.on_connect = on_connect

    print(f"Connecting to MQTT broker at {broker}:{port}...")
    try:
        client.connect(broker, port, 60)
        client.loop_start()

        time.sleep(2)  # wait for connection to establish

        print("\nPublishing MQTT Discovery configurations...")
        publish_discovery_config(client, device_name, sensor_type=sensor_type, unitOfMeasurement="°C", device_class="temperature")
        publish_discovery_config(client, device_name, sensor_type=sensor_type, unitOfMeasurement="%", device_class="humidity")
        

        print(f"\nStarting continuous publish loop (every {update_interval} seconds)...")
        print("Press Ctrl+C to stop\n")

        ## Continuous publish loop; read sensor and publish data

    except KeyboardInterrupt:
        print("\n\nStopping publisher...")
        client.loop_stop()
        client.disconnect()
        print("Disconnected from MQTT broker")

    except Exception as e:
        print(f"Error: {e}")
        client.loop_stop()
        client.disconnect()



if __name__ == "__main__":
    main()
