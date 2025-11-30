# Branching Strategy

This document describes the branching strategy used in this project, following a modified Git Flow model optimized for continuous delivery.

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
  
release/1.1.0 (preparation)


## Branch Types

### 1. `main` Branch

**Purpose:** Production-ready code

**Characteristics:**
- Always stable and deployable
- Protected branch (requires PR and reviews)
- All commits are tagged with version numbers
- Direct commits are not allowed
- Triggers production deployment pipeline

**Merges from:**
- `release/*` branches (normal releases)


### 2. `develop` Branch

**Purpose:** Integration branch for ongoing development

**Characteristics:**
- Contains latest completed development features
- Should always be in a working state
- Automatically deployed to development/staging environment
- Base branch for new features

**Merges from:**
- `feature/*` branches (new features)
- `release/*` branches (after release to main)

**Merges to:**
- `release/*` branches

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

### 4. `release/*` Branches

**Purpose:** Prepare for production release

**Naming Convention:**
```
release/X.Y.Z
```

**Examples:**
- `release/1.0.0`
- `release/1.1.0`
- `release/2.0.0`

**Workflow:**
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/1.1.0

# Prepare release
# - Update version numbers
# - Update CHANGELOG.md
# - Fix release-specific bugs
# - Update documentation

# When ready, merge to main
git checkout main
git pull origin main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git pull origin develop
git merge --no-ff release/1.1.0
git push origin develop

# Delete release branch
git branch -d release/1.1.0
git push origin --delete release/1.1.0
```

**Merges from:** `develop`

**Merges to:** `main` and `develop`


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
# 1. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/1.1.0

# 2. Prepare release
# - Update version in files
# - Update CHANGELOG.md
# - Fix any last-minute bugs
git commit -m "Prepare release 1.1.0"

# 3. Merge to main
git checkout main
git pull origin main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin main --tags

# 4. Merge back to develop
git checkout develop
git pull origin develop
git merge --no-ff release/1.1.0
git push origin develop

# 5. Clean up
git branch -d release/1.1.0
```

## Quick Reference

```bash
# Start new feature
git checkout develop && git pull
git checkout -b feature/my-feature

# Prepare release
git checkout develop && git pull
git checkout -b release/1.1.0

# Update feature with latest develop
git checkout develop && git pull
git checkout feature/my-feature
git merge develop

# Clean up merged branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```
