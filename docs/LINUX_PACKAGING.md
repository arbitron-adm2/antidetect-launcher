# Linux Packaging Guide

## Overview

Antidetect Launcher supports multiple Linux packaging formats:
- **DEB packages** (Debian/Ubuntu)
- **AppImage** (Universal Linux)
- **Flatpak** (Sandboxed installation)

## DEB Package (.deb)

### Installation Locations

- **Application**: `/opt/antidetect-launcher/`
- **Virtual Environment**: `/opt/antidetect-launcher/venv/`
- **Executables**: `/usr/bin/antidetect-launcher`, `/usr/bin/antidetect-launcher`
- **Data**: `/var/lib/antidetect-launcher/`
- **Logs**: `/var/log/antidetect-launcher/`
- **Cache**: `/var/cache/antidetect-launcher/`
- **Desktop file**: `/usr/share/applications/antidetect-launcher.desktop`
- **Icons**: `/usr/share/icons/hicolor/*/apps/antidetect-launcher.png`

### Building

```bash
# Install build dependencies
sudo apt-get install devscripts debhelper dh-python build-essential python3-all python3-setuptools

# Build the package
cd /path/to/antidetect-launcher
./build/scripts/build_deb.sh build

# The .deb file will be in build/debian/
```

### Installation

```bash
# Install the package
sudo dpkg -i build/debian/antidetect-launcher_0.1.0-1_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Launch GUI
antidetect-launcher

# Or use CLI
antidetect-launcher --help
```

### Uninstallation

```bash
# Remove package but keep configuration
sudo apt-get remove antidetect-launcher

# Complete removal including data
sudo apt-get purge antidetect-launcher
```

### Dependencies

Required packages:
- python3 (>= 3.12)
- python3-pip
- python3-venv
- libqt6core6 or python3-pyqt6
- libnss3, libxss1, libasound2 (for browser)
- libxtst6, libxrandr2, libgbm1
- libgtk-3-0
- xdg-utils

Recommended:
- redis-server (for session management)
- chromium-browser or google-chrome-stable

## AppImage

### Building

```bash
# Install dependencies
sudo apt-get install wget fuse libfuse2

# Build AppImage
./build/scripts/build_appimage.sh

# Output: build/appimage/AntidetectLauncher-0.1.0-x86_64.AppImage
```

### Running

```bash
# Make executable
chmod +x AntidetectLauncher-0.1.0-x86_64.AppImage

# Run
./AntidetectLauncher-0.1.0-x86_64.AppImage
```

### Features

- No installation required
- Runs on any Linux distro
- Self-contained with all dependencies
- Portable - can run from USB drive

## Flatpak

### Building

```bash
# Install Flatpak
sudo apt-get install flatpak flatpak-builder

# Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Build Flatpak
./build/scripts/build_flatpak.sh

# Output: build/flatpak/com.antidetect.Browser-0.1.0.flatpak
```

### Installation

```bash
# Install
flatpak install build/flatpak/com.antidetect.Browser-0.1.0.flatpak

# Run
flatpak run com.antidetect.Browser
```

### Uninstallation

```bash
flatpak uninstall com.antidetect.Browser
```

### Features

- Sandboxed execution
- Automatic updates through Flatpak
- Consistent experience across distros
- Filesystem access controls

## Comparison

| Feature | DEB | AppImage | Flatpak |
|---------|-----|----------|---------|
| Installation | System-wide | Portable | User/System |
| Dependencies | Managed by apt | Bundled | Runtime-based |
| Updates | apt upgrade | Manual | Flatpak update |
| Sandboxing | No | No | Yes |
| File access | Full | Full | Restricted |
| Distro support | Debian/Ubuntu | Universal | Universal |
| Size | Small | Large | Medium |

## Permissions

### DEB Package Permissions

Post-installation:
- `/opt/antidetect-launcher/`: 755 (readable by all)
- `/var/lib/antidetect-launcher/`: 755 (user data)
- `/var/log/antidetect-launcher/`: 755 (log files)
- Executables: 755

### Security Considerations

1. **Virtual Environment**: Isolated Python dependencies
2. **User Data**: Stored in `/var/lib/antidetect-launcher/`
3. **Logs**: Accessible in `/var/log/antidetect-launcher/`
4. **No SUID**: No setuid binaries included
5. **Desktop Integration**: Standard XDG desktop file

## Troubleshooting

### DEB Package Issues

**Missing dependencies:**
```bash
sudo apt-get install -f
```

**Icon not showing:**
```bash
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
sudo update-desktop-database
```

**Playwright browser not found:**
```bash
/opt/antidetect-launcher/venv/bin/playwright install chromium
```

### AppImage Issues

**FUSE not available:**
```bash
# Extract and run
./AntidetectLauncher-0.1.0-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun
```

### Flatpak Issues

**Permissions denied:**
```bash
# Grant additional permissions
flatpak override --user --filesystem=home com.antidetect.Browser
```

## Automated Building

### GitHub Actions

See `.github/workflows/build-linux.yml` for automated builds.

### Local Build Script

```bash
# Build all formats
./build/scripts/build_all_linux.sh
```

## Distribution

### DEB Repository

Coming soon: APT repository for automatic updates.

### Flathub

Submit to Flathub for distribution through Flatpak.

### AppImage Hub

List on AppImageHub for discoverability.

## Development

### Testing the Package

```bash
# Test DEB in Docker
docker run -it ubuntu:22.04
# Install package and test

# Test installation script
./build/scripts/build_deb.sh clean
./build/scripts/build_deb.sh build
sudo ./build/scripts/build_deb.sh install
```

### Lintian Checks

```bash
lintian build/debian/antidetect-launcher_0.1.0-1_amd64.deb
```

### Package Quality

- Follows Debian Policy 4.6.2
- Debhelper compatibility level 13
- Proper maintainer scripts
- Clean uninstallation
- Desktop file validation

## Support

For packaging issues, please report at:
https://github.com/antidetect/antidetect-launcher/issues
