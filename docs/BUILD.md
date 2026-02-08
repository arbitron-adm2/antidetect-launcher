# Build & Deployment Guide

Complete guide for building and deploying Antidetect Browser across platforms.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development Builds](#local-development-builds)
- [Platform-Specific Builds](#platform-specific-builds)
- [CI/CD Pipeline](#cicd-pipeline)
- [Version Management](#version-management)
- [Release Process](#release-process)
- [Auto-Update System](#auto-update-system)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Git
- Platform-specific tools (see below)

### Build All Platforms

```bash
# Linux/macOS
chmod +x scripts/build_local.sh
./scripts/build_local.sh

# Windows
python scripts/build_local.py
```

---

## Local Development Builds

### Build Executable Only

Build standalone executable for current platform:

```bash
# Linux/macOS
./scripts/build.sh

# Windows
scripts\build.bat
```

Output:
- Linux: `dist/AntidetectBrowser/AntidetectBrowser`
- macOS: `dist/AntidetectBrowser.app`
- Windows: `dist/AntidetectBrowser/AntidetectBrowser.exe`

### Build Distributable Package

```bash
# Linux - .deb package
./scripts/build_deb.sh

# macOS - .dmg installer
./scripts/build_dmg.sh

# Windows - .exe installer
python scripts/build_installer.py
```

### Clean Build

Remove all build artifacts:

```bash
./scripts/build_local.sh --clean
```

---

## Platform-Specific Builds

### Linux (.deb)

#### Requirements
```bash
sudo apt-get install -y \
    libqt6core6 libqt6gui6 libqt6widgets6 libqt6svg6 \
    dpkg-dev fakeroot
```

#### Build Process
```bash
# 1. Build executable
./scripts/build.sh

# 2. Create .deb package
./scripts/build_deb.sh
```

#### Install Package
```bash
sudo dpkg -i dist/antidetect-browser_0.1.0_amd64.deb
sudo apt-get install -f  # Fix dependencies
```

#### Package Contents
- Binary: `/opt/antidetect-browser/AntidetectBrowser`
- Launcher: `/usr/bin/antidetect-browser`
- Desktop file: `/usr/share/applications/antidetect-browser.desktop`
- Icon: `/usr/share/pixmaps/antidetect-browser.png`
- User data: `~/.local/share/antidetect-browser/data/`

### Windows (.exe)

#### Requirements
- [NSIS](https://nsis.sourceforge.io/) (Nullsoft Scriptable Install System)

Install with Chocolatey:
```powershell
choco install nsis
```

#### Build Process
```powershell
# 1. Build executable
scripts\build.bat

# 2. Create installer
python scripts/build_installer.py
```

#### Installer Features
- Installs to `C:\Program Files\AntidetectBrowser`
- Creates Desktop and Start Menu shortcuts
- Adds to Windows Registry (uninstall support)
- User data in `%LOCALAPPDATA%\AntidetectBrowser\data\`

### macOS (.dmg)

#### Requirements
```bash
# Xcode Command Line Tools
xcode-select --install
```

#### Build Process
```bash
# 1. Build .app bundle
./scripts/build.sh

# 2. Create .dmg installer
./scripts/build_dmg.sh
```

#### App Bundle Structure
```
AntidetectBrowser.app/
├── Contents/
│   ├── MacOS/
│   │   └── AntidetectBrowser
│   ├── Resources/
│   ├── Info.plist
│   └── ...
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Continuous Integration (`ci.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests

**Jobs:**
- **Test**: Run tests on Ubuntu, Windows, macOS
- **Lint**: Code quality checks (ruff, mypy)
- **Security Scan**: Vulnerability checks (bandit, safety)

#### 2. Build & Release (`build.yml`)

**Triggers:** Git tags (`v*.*.*`), Manual workflow dispatch

**Jobs:**
1. **build-windows**: Build Windows .exe installer
2. **build-linux**: Build Linux .deb package
3. **build-macos**: Build macOS .dmg installer
4. **create-release**: Create GitHub Release with artifacts
5. **publish-update-manifest**: Generate auto-update manifest

### Workflow Files

```
.github/workflows/
├── ci.yml              # Continuous Integration
└── build.yml           # Build & Release
```

---

## Version Management

### Bump Version

```bash
# Patch version (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Minor version (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Major version (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py 1.2.3
```

This updates:
- `pyproject.toml` - Project version
- `antidetect-browser.spec` - PyInstaller bundle version

### Version Files

Version is stored in:
- `pyproject.toml` - Source of truth

```toml
[project]
version = "0.1.0"
```

---

## Release Process

### Automated Release (Recommended)

1. **Bump version**
```bash
python scripts/bump_version.py minor
```

2. **Commit and tag**
```bash
git add pyproject.toml antidetect-browser.spec
git commit -m "Bump version to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
```

3. **Push to trigger CI/CD**
```bash
git push origin main
git push origin v0.2.0
```

4. **GitHub Actions will:**
   - Build for all platforms
   - Run tests
   - Generate changelog
   - Create GitHub Release
   - Upload artifacts
   - Publish update manifest

### Manual Release

If you need to build locally and create release manually:

```bash
# 1. Build all platforms (requires each OS)
./scripts/build_local.sh

# 2. Generate changelog
python scripts/generate_changelog.py 0.2.0 > CHANGELOG.md

# 3. Create GitHub Release manually
gh release create v0.2.0 \
    --title "Release v0.2.0" \
    --notes-file CHANGELOG.md \
    dist/AntidetectBrowser-Setup-*.exe \
    dist/antidetect-browser_*.deb \
    dist/AntidetectBrowser-macOS-*.dmg
```

---

## Auto-Update System

### Update Manifest

Generated automatically on release:

```json
{
  "version": "0.2.0",
  "release_date": "2024-01-15",
  "release_notes_url": "https://github.com/antidetect/antidetect-playwright/releases/tag/v0.2.0",
  "platforms": {
    "windows": {
      "url": "https://github.com/.../AntidetectBrowser-Setup-0.2.0.exe",
      "sha256": "abc123...",
      "size": 52428800,
      "type": "installer"
    },
    "linux": {
      "url": "https://github.com/.../antidetect-browser_0.2.0_amd64.deb",
      "sha256": "def456...",
      "size": 48234567,
      "type": "deb"
    },
    "macos": {
      "url": "https://github.com/.../AntidetectBrowser-macOS-0.2.0.dmg",
      "sha256": "ghi789...",
      "size": 51234567,
      "type": "dmg"
    }
  }
}
```

### Integration in Application

```python
from antidetect_playwright.updater import UpdateChecker

# Initialize
updater = UpdateChecker("0.1.0", data_dir)

# Check for updates
update_info = await updater.check_for_updates()
if update_info:
    print(f"Update available: {update_info['version']}")

    # Download update
    file_path = await updater.download_update(update_info)

    # Verify integrity
    if updater.verify_download(file_path, update_info['sha256']):
        # Prompt user to install
        pass
```

### Update Manifest Location

- Production: `https://raw.githubusercontent.com/antidetect/antidetect-playwright/main/update-manifest.json`
- Development: Local file system

---

## Build Scripts Reference

### Main Scripts

| Script | Description |
|--------|-------------|
| `build.sh` | Build executable for current platform |
| `build_deb.sh` | Create Linux .deb package |
| `build_dmg.sh` | Create macOS .dmg installer |
| `build_installer.py` | Create Windows NSIS installer |
| `build_local.sh` | Build all artifacts for current platform |
| `bump_version.py` | Version management |
| `generate_changelog.py` | Generate release changelog |
| `generate_update_manifest.py` | Create update manifest |

### Helper Scripts

| Script | Description |
|--------|-------------|
| `generate_icons.py` | Convert SVG to platform icons |
| `install_linux.sh` | Install dependencies on Linux |
| `fix_camoufox_linux.sh` | Fix Camoufox permissions on Linux |

---

## Environment Variables

### Build Configuration

```bash
# Python version
export PYTHON_VERSION=3.12

# PyInstaller options
export PYINSTALLER_ARGS="--clean --noconfirm"

# NSIS path (Windows)
export NSIS_PATH="C:\Program Files (x86)\NSIS\makensis.exe"
```

### Runtime Configuration

```bash
# Data directory override
export ANTIDETECT_DATA_DIR="$HOME/.antidetect-browser"

# Update check interval (seconds)
export ANTIDETECT_UPDATE_CHECK_INTERVAL=3600

# Disable auto-update
export ANTIDETECT_DISABLE_UPDATE=1
```

---

## Troubleshooting

### Build Issues

#### PyInstaller "Module not found"
```bash
# Add to hiddenimports in antidetect-browser.spec
hiddenimports = [
    'missing_module',
]
```

#### Icon not found
```bash
# Regenerate icons
python scripts/generate_icons.py
```

#### Permission denied on Linux
```bash
# Fix permissions
chmod +x scripts/*.sh
./scripts/fix_camoufox_linux.sh
```

### Package Issues

#### .deb dependencies
```bash
# Fix broken dependencies
sudo apt-get install -f
```

#### Windows installer fails
```bash
# Check NSIS installation
where makensis

# Install NSIS
choco install nsis
```

#### macOS code signing
```bash
# For development, allow unsigned apps
xattr -cr dist/AntidetectBrowser.app
```

---

## Best Practices

### Pre-Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Run full test suite: `pytest tests/`
- [ ] Test builds on all platforms
- [ ] Update documentation
- [ ] Review security scan results
- [ ] Generate changelog
- [ ] Tag release in git

### Security

- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Verify package signatures before release
- Run security scans (bandit, safety)

### Performance

- Use `--clean` flag for final builds
- Enable UPX compression in .spec file
- Strip debug symbols on Linux
- Test startup time on each platform

---

## Support

- **Issues**: https://github.com/antidetect/antidetect-playwright/issues
- **Documentation**: https://github.com/antidetect/antidetect-playwright/docs
- **Releases**: https://github.com/antidetect/antidetect-playwright/releases
