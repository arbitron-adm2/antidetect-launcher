## Linux Packaging Quick Start

### Build DEB Package

```bash
# One-step build
./build/scripts/build_deb.sh build

# Output: build/debian/antidetect-launcher_0.1.0-1_amd64.deb
```

### Install

```bash
# Install DEB
sudo dpkg -i build/debian/antidetect-launcher_0.1.0-1_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Run
antidetect-launcher
```

### Alternative Formats

```bash
# Build AppImage (portable)
./build/scripts/build_appimage.sh
./build/appimage/AntidetectLauncher-0.1.0-x86_64.AppImage

# Build Flatpak (sandboxed)
./build/scripts/build_flatpak.sh
flatpak install build/flatpak/com.antidetect.Browser-0.1.0.flatpak
```

### Build All Formats

```bash
./build/scripts/build_all_linux.sh
```

See [LINUX_PACKAGING.md](./LINUX_PACKAGING.md) for detailed documentation.
