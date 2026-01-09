# Changelog

All notable changes to this project will be documented in this file.

## v1.0

### Added
- Initial project setup with Docker containerization
- MQTT auto-discovery for Home Assistant integration
- Automated CI/CD pipeline with GitHub Actions
- Multi-platform Docker builds (ARM64)
- Comprehensive test suite with pytest
- Configuration via YAML file
- Docker Compose setup for easy deployment
- Default config embedded in Docker image for pre-built image support
- Volume mount in docker-compose.yml for custom config override

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## v1.1
### Fixed
- fixed an error in the docker-compose file where the eocker-compose file did not get the correct image from the repository
