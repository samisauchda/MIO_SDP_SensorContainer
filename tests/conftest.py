import pytest
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'mqtt': {
            'broker': 'test.mosquitto.org',
            'port': 1883,
            'username': 'test_user',
            'password': 'test_pass'
        },
        'device': {
            'name': 'Test Sensor'
        },
        'sensors': [
            {
                'type': 'dht11',
                'enabled': True,
                'update_interval': 60,
                'GPIO_pin_RPI': 4
            }
        ]
    }


@pytest.fixture
def sample_config_file(tmp_path, sample_config):
    """Create a temporary config file for testing"""
    import yaml

    config_file = tmp_path / "test_config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)

    return str(config_file)
