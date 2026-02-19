# Packaging Structure

This directory contains all packaging configurations for Antidetect Launcher.

## Directory Structure

```
build/
├── scripts/
│   ├── build_deb.sh          # Build DEB package
│   ├── build_appimage.sh     # Build AppImage
│   ├── build_flatpak.sh      # Build Flatpak
│   ├── build_all_linux.sh    # Build all Linux packages
│   └── test_deb.sh           # Test DEB package
├── linux/
│   └── antidetect-launcher.desktop  # Desktop file
└── icons/
    └── linux/                # Icon files

debian/
├── control                   # Package metadata and dependencies
├── rules                     # Build instructions
├── changelog                 # Version history
├── copyright                 # License information
├── compat                    # Debhelper compatibility level
├── install                   # Files to install
├── postinst                  # Post-installation script
├── prerm                     # Pre-removal script
├── postrm                    # Post-removal script
├── triggers                  # Icon cache triggers
├── apparmor/                 # AppArmor security profile
└── source/
    └── format                # Source package format
```

## Quick Commands

### DEB Package

```bash
# Build
./build/scripts/build_deb.sh build

# Test
./build/scripts/test_deb.sh build/debian/antidetect-launcher_0.1.0-1_amd64.deb

# Install
sudo dpkg -i build/debian/antidetect-launcher_0.1.0-1_amd64.deb
```

### AppImage

```bash
# Build
./build/scripts/build_appimage.sh

# Run
chmod +x build/appimage/AntidetectLauncher-0.1.0-x86_64.AppImage
./build/appimage/AntidetectLauncher-0.1.0-x86_64.AppImage
```

### Flatpak

```bash
# Build
./build/scripts/build_flatpak.sh

# Install and run
flatpak install build/flatpak/com.antidetect.launcher-0.1.0.flatpak
flatpak run com.antidetect.launcher
```

## Package Comparison

| Feature | DEB | AppImage | Flatpak |
|---------|-----|----------|---------|
| Installation | System | Portable | User/System |
| Updates | apt | Manual | Automatic |
| Size | ~50MB | ~200MB | ~100MB |
| Sandboxing | No | No | Yes |
| Best for | Ubuntu/Debian | Any distro | Security-focused |

## Installation Paths

### DEB Package
- Application: `/opt/antidetect-launcher/`
- Executables: `/usr/bin/antidetect-launcher`
- Data: `/var/lib/antidetect-launcher/`
- Config: `/etc/antidetect-launcher/`

### AppImage
- Self-contained in AppImage file
- User data: `~/.config/antidetect-launcher/`

### Flatpak
- App: `/var/lib/flatpak/app/com.antidetect.launcher/`
- User data: `~/.var/app/com.antidetect.launcher/`

## Dependencies

Required for building:
- debhelper (>= 13)
- dh-python
- python3 (>= 3.12)
- python3-setuptools
- build-essential

Runtime dependencies:
- python3 (>= 3.12)
- libqt6core6, libqt6gui6, libqt6widgets6, libqt6svg6
- libnss3, libxss1, libasound2
- libxtst6, libxrandr2, libgbm1

## CI/CD

GitHub Actions workflow: `.github/workflows/build-linux.yml`

Builds on:
- Push to main/develop
- Pull requests
- Version tags (v*)

Artifacts uploaded for each build.

## Documentation

- [LINUX_PACKAGING.md](../docs/LINUX_PACKAGING.md) - Complete guide
- [LINUX_QUICK_START.md](../docs/LINUX_QUICK_START.md) - Quick start

## Maintenance

### Update Version

1. Edit `debian/changelog`:
   ```bash
   dch -v 0.2.0-1 "New version"
   ```

2. Update `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

3. Rebuild packages

### Test in Docker

```bash
docker run -it ubuntu:22.04 bash
# Inside container:
apt-get update
apt-get install -y ./antidetect-launcher_0.1.0-1_amd64.deb
antidetect-launcher
```

## Publishing

### APT Repository (Future)

Will host packages at: `https://packages.antidetect.io/`

### Flathub

Submit `com.antidetect.launcher` to Flathub for distribution.

### Snap Store

Snap packaging coming soon.

## Support

For packaging issues:
- GitHub Issues: https://github.com/antidetect/antidetect-launcher/issues
- Tag: `packaging`, `linux`
