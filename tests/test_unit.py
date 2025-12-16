import pytest
import json
import yaml
from unittest.mock import Mock, patch, MagicMock
import sensor_container


class TestLoadConfig:
    """Test the load_config function"""

    def test_load_config_success(self, sample_config_file, sample_config):
        """Test loading a valid config file"""
        config = sensor_container.load_config(sample_config_file)

        assert config == sample_config
        assert config['mqtt']['broker'] == 'test.mosquitto.org'
        assert config['mqtt']['port'] == 1883
        assert config['device']['name'] == 'Test Sensor'

    def test_load_config_file_not_found(self):
        """Test loading a non-existent config file"""
        with pytest.raises(FileNotFoundError):
            sensor_container.load_config('nonexistent.yml')

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading an invalid YAML file"""
        invalid_file = tmp_path / "invalid.yml"
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            sensor_container.load_config(str(invalid_file))


class TestOnConnect:
    """Test the on_connect callback function"""

    def test_on_connect_success(self, capsys):
        """Test successful connection callback"""
        mock_client = Mock()
        mock_userdata = None
        mock_flags = {}
        rc = 0  # Success code

        sensor_container.on_connect(mock_client, mock_userdata, mock_flags, rc)

        captured = capsys.readouterr()
        assert "Connected to MQTT Broker successfully!" in captured.out

    def test_on_connect_failure(self, capsys):
        """Test failed connection callback"""
        mock_client = Mock()
        mock_userdata = None
        mock_flags = {}
        rc = 5  # Connection refused

        sensor_container.on_connect(mock_client, mock_userdata, mock_flags, rc)

        captured = capsys.readouterr()
        assert "Failed to connect, return code 5" in captured.out


class TestPublishDiscoveryConfig:
    """Test the publish_discovery_config function"""

    def test_publish_discovery_config_basic(self):
        """Test basic discovery config publishing"""
        mock_client = Mock()
        mock_client.publish.return_value = (0, 1)  # Success

        device_name = "Living Room Sensor"
        sensor_type = "temperature"

        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            sensor_type,
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        # Verify publish was called
        assert mock_client.publish.called
        call_args = mock_client.publish.call_args

        # Check topic format
        topic = call_args[0][0]
        assert topic == "homeassistant/sensor/living_room_sensor_temperature/config"

        # Check payload
        payload = json.loads(call_args[0][1])
        assert payload['name'] == "Living Room Sensor Temperature"
        assert payload['unique_id'] == "living_room_sensor_temperature"
        assert payload['state_topic'] == "homeassistant/sensor/living_room_sensor/temperature/state"

        # Check retain flag
        assert call_args[1]['retain'] is True

    def test_publish_discovery_config_device_info(self):
        """Test device information in discovery config"""
        mock_client = Mock()
        mock_client.publish.return_value = (0, 1)

        device_name = "Test Device"
        sensor_type = "humidity"

        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            sensor_type,
            unitOfMeasurement="%",
            device_class="humidity"
        )

        call_args = mock_client.publish.call_args
        payload = json.loads(call_args[0][1])

        # Check device info
        assert 'device' in payload
        device = payload['device']
        assert device['name'] == "Test Device"
        assert device['model'] == "humidity Sensor"
        assert device['manufacturer'] == "Custom"
        assert device['unit_of_measurement'] == "%"
        assert device['device_class'] == "humidity"

    def test_publish_discovery_config_device_id_formatting(self):
        """Test device ID formatting (lowercase, spaces to underscores)"""
        mock_client = Mock()
        mock_client.publish.return_value = (0, 1)

        device_name = "My Test Device"
        sensor_type = "temperature"

        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            sensor_type
        )

        call_args = mock_client.publish.call_args
        topic = call_args[0][0]

        # Verify device_id is lowercase with underscores
        assert "my_test_device" in topic

    def test_publish_discovery_config_failure(self, capsys):
        """Test publishing failure handling"""
        mock_client = Mock()
        mock_client.publish.return_value = (1, 1)  # Failure

        sensor_container.publish_discovery_config(
            mock_client,
            "Test",
            "temperature"
        )

        captured = capsys.readouterr()
        assert "Failed to publish discovery config" in captured.out

    def test_publish_discovery_config_success_message(self, capsys):
        """Test success message on publish"""
        mock_client = Mock()
        mock_client.publish.return_value = (0, 1)  # Success

        sensor_container.publish_discovery_config(
            mock_client,
            "Test",
            "humidity"
        )

        captured = capsys.readouterr()
        assert "Published discovery config for humidity" in captured.out

    def test_publish_discovery_config_different_sensor_types(self):
        """Test publishing configs for different sensor types"""
        mock_client = Mock()
        mock_client.publish.return_value = (0, 1)

        device_name = "Multi Sensor"

        # Test temperature
        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            "temperature",
            unitOfMeasurement="°C",
            device_class="temperature"
        )

        temp_call = mock_client.publish.call_args_list[0]
        temp_payload = json.loads(temp_call[0][1])
        assert "Temperature" in temp_payload['name']

        # Test humidity
        sensor_container.publish_discovery_config(
            mock_client,
            device_name,
            "humidity",
            unitOfMeasurement="%",
            device_class="humidity"
        )

        humidity_call = mock_client.publish.call_args_list[1]
        humidity_payload = json.loads(humidity_call[0][1])
        assert "Humidity" in humidity_payload['name']
