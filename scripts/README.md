# Build Scripts Directory

Automated build and deployment scripts for Antidetect Browser.

## Scripts Overview

### Build Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `build.sh` | All | Build executable for current platform |
| `build_deb.sh` | Linux | Create .deb package |
| `build_dmg.sh` | macOS | Create .dmg installer |
| `build_installer.py` | Windows | Create NSIS .exe installer |
| `build_local.sh` | All | Universal build script for current platform |

### Utility Scripts

| Script | Description |
|--------|-------------|
| `bump_version.py` | Bump project version (major/minor/patch) |
| `generate_changelog.py` | Generate release changelog from git commits |
| `generate_update_manifest.py` | Create update manifest for auto-update |
| `generate_icons.py` | Convert SVG icon to platform-specific formats |
| `install_linux.sh` | Install system dependencies on Linux |
| `fix_camoufox_linux.sh` | Fix Camoufox browser permissions on Linux |

## Quick Start

### Build for Current Platform

```bash
# Full build (executable + package)
./scripts/build_local.sh

# Executable only
./scripts/build.sh

# Package only
./scripts/build_local.sh --package

# Clean build
./scripts/build_local.sh --clean
```

### Version Management

```bash
# Bump version
python scripts/bump_version.py patch   # 0.1.0 -> 0.1.1
python scripts/bump_version.py minor   # 0.1.0 -> 0.2.0
python scripts/bump_version.py major   # 0.1.0 -> 1.0.0

# Set specific version
python scripts/bump_version.py 1.2.3
```

### Release Automation

```bash
# Generate changelog for release
python scripts/generate_changelog.py 0.2.0

# Generate update manifest
python scripts/generate_update_manifest.py 0.2.0
```

## Platform-Specific Builds

### Linux (.deb)

```bash
# Prerequisites
sudo apt-get install -y libqt6core6 libqt6gui6 dpkg-dev

# Build
./scripts/build.sh              # Build executable
./scripts/build_deb.sh          # Create .deb package

# Install
sudo dpkg -i dist/antidetect-browser_0.1.0_amd64.deb
```

### Windows (.exe)

```powershell
# Prerequisites
choco install nsis

# Build
scripts\build.bat               # Build executable
python scripts/build_installer.py  # Create installer

# Install
dist\AntidetectBrowser-Setup-0.1.0.exe
```

### macOS (.dmg)

```bash
# Prerequisites
xcode-select --install

# Build
./scripts/build.sh              # Build .app bundle
./scripts/build_dmg.sh          # Create .dmg

# Install
open dist/AntidetectBrowser-macOS-0.1.0.dmg
```

## Script Details

### build.sh

Builds standalone executable using PyInstaller.

**Usage:**
```bash
./scripts/build.sh
```

**Output:**
- Linux: `dist/AntidetectBrowser/AntidetectBrowser`
- macOS: `dist/AntidetectBrowser.app`
- Windows: `dist/AntidetectBrowser/AntidetectBrowser.exe`

**Requirements:**
- Virtual environment with package dependencies installed
- Generated icons (runs `generate_icons.py` automatically)

### build_deb.sh

Creates Debian package for Ubuntu/Debian systems.

**Usage:**
```bash
./scripts/build_deb.sh
```

**Output:** `dist/antidetect-browser_0.1.0_amd64.deb`

**Package includes:**
- Binary in `/opt/antidetect-browser/`
- Launcher script in `/usr/bin/antidetect-browser`
- Desktop file for application menu
- Icon in `/usr/share/pixmaps/`

### build_dmg.sh

Creates macOS disk image installer.

**Usage:**
```bash
./scripts/build_dmg.sh
```

**Output:** `dist/AntidetectBrowser-macOS-0.1.0.dmg`

**Features:**
- Drag-and-drop installer
- Applications folder symlink
- Custom background (optional)

### build_installer.py

Creates Windows NSIS installer.

**Usage:**
```bash
python scripts/build_installer.py
```

**Output:** `dist/AntidetectBrowser-Setup-0.1.0.exe`

**Features:**
- GUI installer wizard
- Desktop and Start Menu shortcuts
- Registry entries
- Uninstaller

### build_local.sh

Universal build script that detects platform and builds accordingly.

**Usage:**
```bash
./scripts/build_local.sh [OPTIONS]

Options:
  --exe          Build executable only
  --package      Build package only
  --clean        Clean before building
```

**Examples:**
```bash
./scripts/build_local.sh                # Build all
./scripts/build_local.sh --clean        # Clean + build all
./scripts/build_local.sh --package      # Package only
```

### bump_version.py

Manages project version across files.

**Usage:**
```bash
python scripts/bump_version.py [major|minor|patch|VERSION]
```

**Examples:**
```bash
python scripts/bump_version.py patch    # 0.1.0 -> 0.1.1
python scripts/bump_version.py minor    # 0.1.0 -> 0.2.0
python scripts/bump_version.py major    # 0.1.0 -> 1.0.0
python scripts/bump_version.py 2.0.0    # Set to 2.0.0
```

**Updates:**
- `pyproject.toml` - Project version
- `antidetect-browser.spec` - Bundle version

### generate_changelog.py

Generates release changelog from git commits.

**Usage:**
```bash
python scripts/generate_changelog.py VERSION
```

**Example:**
```bash
python scripts/generate_changelog.py 0.2.0 > CHANGELOG.md
```

**Categorizes commits by:**
- Features (feat:, add:)
- Bug Fixes (fix:, bug:)
- Performance (perf:, optimize:)
- Documentation (docs:)
- Refactoring (refactor:)
- Tests (test:)
- Chores (chore:, ci:, build:)

### generate_update_manifest.py

Creates JSON manifest for auto-update system.

**Usage:**
```bash
python scripts/generate_update_manifest.py VERSION
```

**Output:** `dist/update-manifest.json`

**Includes:**
- Version information
- Download URLs
- File sizes and SHA256 hashes
- Platform-specific metadata

### generate_icons.py

Converts SVG icon to platform-specific formats.

**Usage:**
```bash
python scripts/generate_icons.py
```

**Generates:**
- Windows: `.ico` (16, 32, 48, 256px)
- macOS: `.icns` (16, 32, 128, 256, 512, 1024px)
- Linux: `.png` (16, 24, 32, 48, 64, 128, 256px)

**Input:** `src/antidetect_playwright/resources/icon.svg`

**Output:** `build/icons/`

## CI/CD Integration

These scripts are used by GitHub Actions workflows:

- **ci.yml**: Runs tests and linters
- **build.yml**: Builds releases for all platforms

See `.github/workflows/` for workflow definitions.

## Development Workflow

1. **Make changes** to code
2. **Test locally**: `pytest tests/`
3. **Build locally**: `./scripts/build_local.sh`
4. **Bump version**: `python scripts/bump_version.py patch`
5. **Commit and tag**:
   ```bash
   git commit -am "Release 0.1.1"
   git tag v0.1.1
   ```
6. **Push to trigger CI/CD**:
   ```bash
   git push origin main --tags
   ```

## Troubleshooting

### "Module not found" during build

Add missing module to `hiddenimports` in `antidetect-browser.spec`:

```python
hiddenimports = [
    'missing_module',
]
```

### "Permission denied" on Linux

```bash
chmod +x scripts/*.sh
```

### Icons not found

```bash
python scripts/generate_icons.py
```

### NSIS not found (Windows)

```powershell
choco install nsis
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHON_VERSION` | Python version for builds | `3.12` |
| `ANTIDETECT_DATA_DIR` | Application data directory | Platform-specific |

## Support

- **Documentation**: `/docs/BUILD.md`
- **Quick Reference**: `/docs/CI_CD_QUICKREF.md`
- **Issues**: GitHub Issues
