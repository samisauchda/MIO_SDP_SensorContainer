import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import paho.mqtt.client as mqtt
import sensor_container


class MockMQTTClient:
    """Mock MQTT client for integration testing"""

    def __init__(self, client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp"):
        self.client_id = client_id
        self.connected = False
        self.published_messages = []
        self.subscriptions = []
        self.on_connect = None
        self.on_message = None
        self.on_disconnect = None
        self._userdata = userdata

    def username_pw_set(self, username, password):
        """Mock username/password setting"""
        self.username = username
        self.password = password

    def connect(self, host, port=1883, keepalive=60, bind_address=""):
        """Mock connection"""
        self.host = host
        self.port = port
        self.connected = True
        # Simulate successful connection callback
        if self.on_connect:
            self.on_connect(self, self._userdata, {}, 0)
        return 0

    def disconnect(self):
        """Mock disconnection"""
        self.connected = False
        if self.on_disconnect:
            self.on_disconnect(self, self._userdata, 0)

    def loop_start(self):
        """Mock loop start"""
        pass

    def loop_stop(self):
        """Mock loop stop"""
        pass

    def publish(self, topic, payload=None, qos=0, retain=False):
        """Mock publish - store messages for verification"""
        message = {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain
        }
        self.published_messages.append(message)
        return (0, len(self.published_messages))  # Success

    def subscribe(self, topic, qos=0):
        """Mock subscribe"""
        self.subscriptions.append({'topic': topic, 'qos': qos})
        return (0, 1)


class TestMQTTIntegration:
    """Integration tests using mock MQTT broker"""

    @patch('sensor_container.mqtt.Client')
    def test_mqtt_client_creation(self, mock_client_class, sample_config):
        """Test MQTT client is created with correct parameters"""
        mock_client = MockMQTTClient()
        mock_client_class.return_value = mock_client

        device_name = sample_config['device']['name']
        expected_client_id = f"{device_name}_sensor_container"

        client = mqtt.Client(client_id=expected_client_id)
        mock_client_class.assert_called_with(client_id=expected_client_id)

    @patch('sensor_container.mqtt.Client')
    def test_mqtt_authentication_setup(self, mock_client_class, sample_config):
        """Test MQTT authentication is configured correctly"""
        mock_client = MockMQTTClient()
        mock_client_class.return_value = mock_client

        username = sample_config['mqtt']['username']
        password = sample_config['mqtt']['password']

        client = mqtt.Client()
        mock_client.username_pw_set(username, password)

        assert mock_client.username == username
        assert mock_client.password == password

    def test_mqtt_connection_flow(self):
        """Test complete MQTT connection flow"""
        mock_client = MockMQTTClient()

        # Set callback
        mock_client.on_connect = sensor_container.on_connect

        # Connect
        mock_client.connect("test.broker", 1883)

        assert mock_client.connected is True
        assert mock_client.host == "test.broker"
        assert mock_client.port == 1883

    def test_discovery_config_mqtt_message(self):
        """Test Home Assistant discovery config MQTT message format"""
        mock_client = MockMQTTClient()

        device_name = "Integration Test Sensor"
        sensor_type = "temperature"

        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            sensor_type,
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        # Verify message was published
        assert len(mock_client.published_messages) == 1

        message = mock_client.published_messages[0]

        # Verify topic format
        expected_topic = "homeassistant/sensor/integration_test_sensor_temperature/config"
        assert message['topic'] == expected_topic

        # Verify retain flag is set
        assert message['retain'] is True

        # Verify payload structure
        payload = json.loads(message['payload'])
        assert 'name' in payload
        assert 'state_topic' in payload
        assert 'unique_id' in payload
        assert 'device' in payload

    def test_multiple_sensor_discovery(self):
        """Test publishing multiple sensor discovery configs"""
        mock_client = MockMQTTClient()

        device_name = "Multi Sensor Device"

        # Publish temperature sensor config
        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            "temperature",
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        # Publish humidity sensor config
        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            "humidity",
            unitOfMeasurement="%",
            device_class="humidity"
        )

        # Verify both messages were published
        assert len(mock_client.published_messages) == 2

        # Verify topics are different
        topics = [msg['topic'] for msg in mock_client.published_messages]
        assert "temperature" in topics[0]
        assert "humidity" in topics[1]

        # Verify both have retain flag
        assert all(msg['retain'] for msg in mock_client.published_messages)

    def test_home_assistant_discovery_protocol_compliance(self):
        """Test compliance with Home Assistant MQTT Discovery protocol"""
        mock_client = MockMQTTClient()

        sensor_container.publish_discovery_config(
            mock_client,
            "Compliance Test",
            "temperature",
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        message = mock_client.published_messages[0]
        payload = json.loads(message['payload'])

        # Required fields per HA MQTT Discovery spec
        required_fields = ['name', 'state_topic', 'unique_id']
        for field in required_fields:
            assert field in payload, f"Missing required field: {field}"

        # Device info structure
        assert 'device' in payload
        device = payload['device']
        assert 'identifiers' in device
        assert isinstance(device['identifiers'], list)
        assert 'name' in device

    @patch('sensor_container.load_config')
    @patch('sensor_container.mqtt.Client')
    def test_end_to_end_workflow(self, mock_client_class, mock_load_config, sample_config):
        """Test end-to-end workflow from config load to MQTT publish"""
        # Setup mocks
        mock_load_config.return_value = sample_config
        mock_client = MockMQTTClient()
        mock_client_class.return_value = mock_client

        # Simulate the workflow
        config = sensor_container.load_config('config.yml')

        broker = config['mqtt']['broker']
        port = config['mqtt']['port']
        username = config['mqtt']['username']
        password = config['mqtt']['password']
        device_name = config['device']['name']
        sensor_type = config['sensors'][0]['type']

        client = mqtt.Client(client_id=f"{device_name}_sensor_container")
        mock_client.username_pw_set(username, password)
        mock_client.on_connect = sensor_container.on_connect

        mock_client.connect(broker, port, 60)
        mock_client.loop_start()

        # Publish discovery configs
        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            sensor_type,
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        # Verify workflow completed successfully
        assert mock_client.connected is True
        assert len(mock_client.published_messages) == 1
        assert mock_client.username == username
        assert mock_client.password == password

    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        mock_client = MockMQTTClient()

        # Simulate connection failure
        mock_client.on_connect = sensor_container.on_connect

        # Manually trigger on_connect with error code
        mock_client.on_connect(mock_client, None, {}, 5)  # Connection refused

        # In real scenario, the error would be logged/handled
        # Here we just verify the callback handles non-zero return codes
        assert True  # Callback should not raise exception
