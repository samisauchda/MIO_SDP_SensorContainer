# Release Pipeline Setup Guide

This guide explains how to configure the automated release pipeline for building and pushing Docker images to Docker Hub.

## Prerequisites

- GitHub repository with admin access
- Docker Hub account (username: `samisauchda`)
- Git Flow branching strategy in place

## One-Time Setup: GitHub Secrets

The release pipeline requires Docker Hub credentials to push images. These must be configured as GitHub repository secrets.

### Step 1: Generate Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click on your username (top right) → **Account Settings**
3. Navigate to **Security** → **Personal Access Tokens**
4. Click **New Access Token**
5. Configure the token:
   - **Description**: `GitHub Actions - sensor-container`
   - **Access permissions**: **Read, Write**
   - **Repository**: `samisauchda/sensor-container` (optional: scope to specific repo)
6. Click **Generate**
7. **IMPORTANT**: Copy the token immediately (it won't be shown again)

### Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the first secret:
   - **Name**: `DOCKERHUB_USERNAME`
   - **Secret**: `samisauchda`
   - Click **Add secret**
5. Click **New repository secret** again
6. Add the second secret:
   - **Name**: `DOCKERHUB_TOKEN`
   - **Secret**: Paste the token you generated in Step 1
   - Click **Add secret**

### Verify Setup

You should now see two secrets listed:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## Using the Release Pipeline

The release pipeline automatically triggers when you push a git tag following semantic versioning.

### Release Workflow (Following Git Flow)

1. **Create release branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/1.0.0
   ```

2. **Prepare the release**:
   - Update `docs/CHANGELOG.md` with version changes
   - Fix any last-minute bugs
   - Test thoroughly

3. **Merge to main** via Pull Request:
   ```bash
   # Push release branch
   git push origin release/1.0.0

   # Create PR: release/1.0.0 → main
   # Get approval and merge
   ```

4. **Tag the release** on main:
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin main --tags
   ```

5. **Merge back to develop**:
   ```bash
   git checkout develop
   git pull origin develop
   git merge --no-ff release/1.0.0
   git push origin develop

   # Clean up release branch
   git branch -d release/1.0.0
   git push origin --delete release/1.0.0
   ```

6. **Monitor the pipeline**:
   - Go to GitHub → **Actions** tab
   - Watch the "Release Pipeline" workflow
   - Check for successful completion

### What Happens Automatically

When you push a tag (e.g., `v1.0.0`):

1. GitHub Actions triggers the Release Pipeline
2. Version is extracted from tag (`v1.0.0` → `1.0.0`)
3. Docker image is built for ARM64 architecture
4. Two images are pushed to Docker Hub:
   - `samisauchda/sensor-container:1.0.0` (semantic version)
   - `samisauchda/sensor-container:latest` (always points to newest)

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `v1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new sensor support
- `v1.1.1` - Fixed MQTT reconnection bug
- `v2.0.0` - Breaking API changes

## Troubleshooting

### Pipeline fails with "authentication required"

**Cause**: Docker Hub credentials are missing or incorrect

**Solution**:
1. Verify secrets exist in GitHub Settings → Secrets
2. Regenerate Docker Hub token if expired
3. Update `DOCKERHUB_TOKEN` secret with new token

### Build fails on ARM64

**Cause**: QEMU emulation issue or dependency problem

**Solution**:
1. Check Dockerfile for ARM64 compatibility
2. Review build logs in GitHub Actions
3. Test locally with: `docker buildx build --platform linux/arm64 .`

### Tag already exists

**Cause**: Trying to push a tag that already exists

**Solution**:
1. Use a new version number
2. Or delete the old tag if it was a mistake:
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

### Wrong version pushed

**Cause**: Tag format doesn't match `v*` pattern

**Solution**:
- Always prefix tags with `v` (e.g., `v1.0.0`, not `1.0.0`)
- Use semantic versioning format: `vMAJOR.MINOR.PATCH`

## Verifying Releases

### Check Docker Hub

1. Go to https://hub.docker.com/r/samisauchda/sensor-container/tags
2. Verify both tags exist:
   - Semantic version (e.g., `1.0.0`)
   - `latest`
3. Check the image architecture is ARM64

### Test Pull on Raspberry Pi

```bash
# Pull latest
docker pull samisauchda/sensor-container:latest

# Pull specific version
docker pull samisauchda/sensor-container:1.0.0

# Verify architecture
docker image inspect samisauchda/sensor-container:latest | grep Architecture
# Should output: "Architecture": "arm64"
```

### Run Container

```bash
docker run -d \
  --name sensor-container \
  -v $(pwd)/config.yml:/app/config.yml \
  samisauchda/sensor-container:latest
```

## Security Notes

- **Never commit tokens**: Secrets are stored in GitHub's encrypted storage
- **Token rotation**: Regenerate Docker Hub tokens periodically
- **Access scope**: Use repository-scoped tokens when possible
- **Review permissions**: Regularly audit who has access to repository secrets
