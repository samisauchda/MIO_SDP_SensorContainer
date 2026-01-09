# IoT Sensor Node for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A containerized IoT sensor node that automatically integrates with Home Assistant via MQTT Discovery. Built with production-ready practices including automated testing, CI/CD, and comprehensive documentation.

## ✨ Features

- **🔌 Automatic Discovery** - Zero configuration needed in Home Assistant
- **📊 Multiple Sensors** - Support for DHT11/22, and simulated sensors
- **🚀 Production Ready** - Automated testing, CI/CD, and quality checks

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Supported Sensors](#-supported-sensors)
- [Development](#-development)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Home Assistant with MQTT integration
- MQTT broker (like Mosquitto)
- Raspberry Pi (for physical sensor deployment)

### Deployment on Raspberry Pi (Recommended)

Deploy the pre-built Docker image on your Raspberry Pi:

1. **Download deployment files:**
   ```bash
   mkdir ~/sensor-container
   cd ~/sensor-container

   # Download docker-compose.yml and config.example.yml from repository
   wget https://raw.githubusercontent.com/samisauchda/MIO_SDP_SensorContainer/main/docker-compose.yml
   wget https://raw.githubusercontent.com/samisauchda/MIO_SDP_SensorContainer/main/config.example.yml
   ```

2. **Create your configuration:**
   ```bash
   cp config.example.yml config.yml
   # Edit config.yml with your MQTT broker and sensor details
   nano config.yml
   ```

3. **Deploy the container:**
   ```bash
   docker-compose up -d
   ```

4. **Check the logs:**
   ```bash
   docker-compose logs -f
   ```

Your sensors should now appear automatically in Home Assistant! 🎉

### Local Development

For local development and testing:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/samisauchda/MIO_SDP_SensorContainer.git
   cd MIO_SDP_SensorContainer
   ```

2. **Create your config:**
   ```bash
   cp config.example.yml config.yml
   # Edit config.yml with your MQTT broker and sensor details
   ```

3. **Start with development compose file:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Check the logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

## ⚙️ Configuration

### Configuration File

The application uses `config.yml` for all settings. Configuration is handled flexibly:

- **Pre-built Docker images** include a default config (from `config.example.yml`) that works out-of-the-box for testing
- **Production deployment** uses volume mount to override with your custom `config.yml` (recommended)
- **Development** mounts the local directory for live code and config changes

**For Raspberry Pi deployment**, create your own `config.yml` to set MQTT broker credentials and sensor configuration:

```yaml
mqtt:
  broker: "homeassistant.local"
  port: 1883
  username: "your_username"
  password: "your_password"

device:
  name: "Living Room Sensor"

sensors:
  - type: "dht11"
    enabled: true
    update_interval: 60
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mqtt.broker` | MQTT broker hostname/IP | Required |
| `mqtt.port` | MQTT broker port | 1883 |
| `mqtt.username` | MQTT username | Optional |
| `mqtt.password` | MQTT password | Optional |
| `device.name` | Device name in Home Assistant | Required |
| `sensors[].type` | Sensor type (dht22, bme280, simulated) | Required |
| `sensors[].enabled` | Enable/disable sensor | true |
| `sensors[].update_interval` | Update interval in seconds | 60 |

## 🔌 Supported Sensors

| Sensor | Measurements | Interface | Status |
|--------|--------------|-----------|--------|
| DHT11/22 | Temperature, Humidity | GPIO | ✅ Supported |
| Simulated | Random test data | N/A | ✅ Supported |

## 🛠️ Development

### Setup Development Environment

```bash
# manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```


## 🏗️ Architecture

```
┌─────────────────────┐
│   Sensor Node       │
│   (Docker)          │
│                     │
│  ┌──────────────┐   │
│  │  Sensors     │   │
│  └──────┬───────┘   │
│         │           │
│  ┌──────▼───────┐   │
│  │ MQTT Client  │   │
│  └──────────────┘   │
└──────────┬──────────┘
           │
           │ MQTT
           ▼
┌──────────────────────┐
│  Home Assistant      │
│  (Auto-discovery)    │
└──────────────────────┘
```

### Project Structure

```
.
├── app/                    # Application code
│   └── sensor_container.py # Sensor and MQTT code
├── docs/                   # Documentation
├── .github/                # GitHub templates and workflows
│   ├── workflows/          # CI/CD pipelines
├── docker-compose.yml      # Production deployment (uses pre-built image)
├── docker-compose.dev.yml  # Development (builds locally)
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── config.example.yml      # Example configuration
├── LICENSE                 # License Info
└── README.md               # This file
```

## 📚 Documentation

- **[BRANCHING_STRATEGY.md](docs/BRANCHING_STRATEGY.md)** - Detailed Git branching model
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Version history and changes
- **[LICENSE](LICENSE)** - MIT License

## 🌳 Branching Strategy

We use a modified Git Flow:

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features

See [BRANCHING_STRATEGY.md](docs/BRANCHING_STRATEGY.md) for detailed workflow.

## 🔐 Security

Security is a priority. 

- Reporting vulnerabilities
- Security best practices
- Supported versions

**Never commit sensitive information like passwords or API keys!**


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

- **Bug Reports:** [Open an issue](https://github.com/samisauchda/MIO_SDP_SensorContainer/issues/new?template=bug_report.md)
- **Feature Requests:** [Open an issue](https://github.com/samisauchda/MIO_SDP_SensorContainer/issues/new?template=feature_request.md)

