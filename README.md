# Sensor Data Simulation

This project implements a simulated IoT sensor that periodically publishes
temperature and humidity readings via MQTT.  
It is intended to test data flow and system integration **without requiring real hardware**.

---

## Requirements

- Python 3.x
- MQTT broker installed locally (e.g., Mosquitto)

Install required Python packages:

```bash
pip install paho-mqtt pyyaml
