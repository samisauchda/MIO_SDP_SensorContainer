# Branching Strategy

This document describes the branching strategy used in this project, following a simplified GitHub Flow model optimized for continuous delivery.

## Branch Overview

```
main (production)
  ├── v1.0.0 (tag)
  ├── v1.1.0 (tag)
  └── v2.0.0 (tag)

develop (integration)
  ├── feature/mqtt-reconnect
  ├── feature/sensor-bme280
  └── feature/web-dashboard
```


## Branch Types

### 1. `main` Branch

**Purpose:** Production-ready code

**Characteristics:**
- Always stable and deployable
- Protected branch (requires PR and reviews)
- Release commits are tagged with version numbers
- Direct commits are not allowed
- Triggers production deployment pipeline

**Merges from:**
- `develop` branch (for releases)

**Versioning:**
- After merging to main, tag the commit with semantic version
- Tags trigger automated Docker image builds and pushes


### 2. `develop` Branch

**Purpose:** Integration branch for ongoing development

**Characteristics:**
- Contains latest completed development features
- Should always be in a working state
- Automatically tested via CI/CD
- Base branch for new features

**Merges from:**
- `feature/*` branches (new features)
- `main` (to keep in sync after releases)

**Merges to:**
- `main` (when ready for release)

**Lifetime:** Permanent

### 3. `feature/*` Branches

**Purpose:** Develop new features and enhancements

**Naming Convention:**
```
feature/short-description
feature/issue-123-description
```

**Examples:**
- `feature/mqtt-retry-logic`
- `feature/web-config-ui`
- `feature/issue-45-add-logging`

**Workflow:**
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/sensor-bme280

# Work on feature
# ... make changes ...
git add .
git commit -m "Add BME280 sensor support"

# Keep up to date with develop
git checkout develop
git pull origin develop
git checkout feature/sensor-bme280
git merge develop

# Push and create PR
git push origin feature/sensor-bme280
# Create PR on GitHub: feature/sensor-bme280 → develop
```

**Merges from:** `develop` (to stay current)

**Merges to:** `develop`

**Lifetime:** Temporary (deleted after PR merge)


## Complete Workflow Examples

### Example 1: Adding a New Feature

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-bme280

# 3. Develop and commit
# ... work work work ...
git commit -m "Add BME280 sensor driver"
git commit -m "Add tests for BME280"
git commit -m "Update documentation"

# 4. Keep up to date
git checkout develop
git pull origin develop
git checkout feature/add-bme280
git merge develop

# 5. Push and create PR
git push origin feature/add-bme280
# Create PR on GitHub: feature/add-bme280 → develop

# 6. After PR approval and merge
git checkout develop
git pull origin develop
git branch -d feature/add-bme280
```

### Example 2: Creating a Release

```bash
# 1. Prepare release on develop
git checkout develop
git pull origin develop

# Update CHANGELOG.md with version and changes
# Test thoroughly to ensure everything works

# 2. Create PR from develop to main
# Create PR on GitHub: develop → main
# Get approval and merge

# 3. Tag the merge commit on main
git checkout main
git pull origin main
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin --tags

# 4. Sync develop with main (if needed)
git checkout develop
git merge main
git push origin develop

# This triggers the automated release pipeline:
# - Docker image builds for ARM64
# - Pushes to Docker Hub as samisauchda/sensor-container:1.1.0
# - Updates the "latest" tag
```

## Quick Reference

```bash
# Start new feature
git checkout develop && git pull
git checkout -b feature/my-feature

# Update feature with latest develop
git checkout develop && git pull
git checkout feature/my-feature
git merge develop

# Create release
# 1. Merge develop → main via PR
# 2. Tag on main:
git checkout main && git pull
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin --tags

# Clean up merged feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `v1.2.3`)
  - **MAJOR**: Breaking changes
  - **MINOR**: New features, backwards compatible
  - **PATCH**: Bug fixes, backwards compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new sensor support
- `v1.1.1` - Fixed MQTT reconnection bug
- `v2.0.0` - Breaking API changes
