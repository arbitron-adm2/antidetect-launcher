# CI/CD Quick Reference

Quick commands for common build and deployment tasks.

## Development

```bash
# Run tests
pytest tests/

# Lint code
ruff check src/

# Type check
mypy src/antidetect_launcher

# Format code
ruff format src/
```

## Local Builds

```bash
# Build for current platform
./scripts/build_local.sh

# Build executable only
./scripts/build.sh

# Build with clean
./scripts/build_local.sh --clean

# Build package only
./scripts/build_local.sh --package
```

## Version Management

```bash
# Bump patch (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Bump minor (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Bump major (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py 1.2.3
```

## Release Process

```bash
# 1. Bump version
python scripts/bump_version.py minor

# 2. Commit and tag
git add pyproject.toml antidetect-launcher.spec
git commit -m "Bump version to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"

# 3. Push (triggers CI/CD)
git push origin main
git push origin v0.2.0

# 4. GitHub Actions will build and release automatically
```

## Platform-Specific

### Linux
```bash
./scripts/build_deb.sh
sudo dpkg -i dist/antidetect-launcher_*.deb
```

### Windows
```powershell
python scripts/build_installer.py
dist\AntidetectLauncher-Setup-*.exe
```

### macOS
```bash
./scripts/build_dmg.sh
open dist/AntidetectLauncher-macOS-*.dmg
```

## CI/CD Workflows

### Manual Trigger (GitHub Actions)
```bash
# Trigger build workflow manually
gh workflow run build.yml

# Trigger with version
gh workflow run build.yml -f version=0.2.0
```

### View Workflow Status
```bash
# List runs
gh run list

# View specific run
gh run view <run-id>

# Watch run
gh run watch
```

## Troubleshooting

```bash
# Clean all build artifacts
rm -rf build/ dist/ *.egg-info
find . -name "__pycache__" -exec rm -rf {} +

# Fix permissions (Linux)
chmod +x scripts/*.sh

# Regenerate icons
python scripts/generate_icons.py

# Fix Camoufox on Linux
./scripts/fix_camoufox_linux.sh
```

## Environment Setup

```bash
# Create venv
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dev dependencies
pip install -e ".[gui,dev,package]"

# Install Playwright browsers
playwright install chromium
```

## Update System

```bash
# Generate update manifest
python scripts/generate_update_manifest.py 0.2.0

# Generate changelog
python scripts/generate_changelog.py 0.2.0
```

## GitHub CLI Commands

```bash
# Create release
gh release create v0.2.0 \
  --title "Release v0.2.0" \
  --notes "Release notes here" \
  dist/*

# Upload assets to existing release
gh release upload v0.2.0 dist/*

# View releases
gh release list

# Delete release
gh release delete v0.2.0
```
