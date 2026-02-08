#!/bin/bash
# Create .deb package for Antidetect Browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION="0.1.0"
ARCH="amd64"
PACKAGE_NAME="antidetect-browser"
DEB_DIR="${PROJECT_ROOT}/dist/deb"
BUILD_DIR="${DEB_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "=== Creating .deb package ==="
echo "Version: $VERSION"
echo "Architecture: $ARCH"
echo

# Check if dist/AntidetectBrowser exists
if [ ! -d "$PROJECT_ROOT/dist/AntidetectBrowser" ]; then
    echo "ERROR: dist/AntidetectBrowser not found!"
    echo "Run ./scripts/build.sh first to build the application."
    exit 1
fi

# Clean old build
rm -rf "$DEB_DIR"
mkdir -p "$BUILD_DIR"

# Create DEBIAN control directory
mkdir -p "$BUILD_DIR/DEBIAN"

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << 'EOL'
Package: antidetect-browser
Version: 0.1.0
Section: web
Priority: optional
Architecture: amd64
Depends: libqt6core6 (>= 6.2), libqt6gui6 (>= 6.2), libqt6widgets6 (>= 6.2), libqt6svg6 (>= 6.2), libc6 (>= 2.34)
Maintainer: Antidetect Team <noreply@antidetect.local>
Description: Stealth browser automation with anti-detection
 Antidetect Browser provides advanced browser fingerprint management
 and stealth automation capabilities using Camoufox and Playwright.
 .
 Features:
  - Multiple browser profiles with unique fingerprints
  - Proxy rotation and management
  - Folder organization and tagging
  - PyQt6-based modern GUI
EOL

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOL'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/pixmaps 2>/dev/null || true
fi

exit 0
EOL
chmod 755 "$BUILD_DIR/DEBIAN/postinst"

# Create postrm script
cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOL'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

exit 0
EOL
chmod 755 "$BUILD_DIR/DEBIAN/postrm"

# Create directory structure
mkdir -p "$BUILD_DIR/opt/antidetect-browser"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"

# Copy application files
echo "Copying application files..."
cp -r "$PROJECT_ROOT/dist/AntidetectBrowser"/* "$BUILD_DIR/opt/antidetect-browser/"

# Create wrapper script
cat > "$BUILD_DIR/usr/bin/antidetect-browser" << 'EOL'
#!/bin/bash
# Antidetect Browser launcher

# Set data directory to user's home
export ANTIDETECT_DATA_DIR="$HOME/.local/share/antidetect-browser/data"
mkdir -p "$ANTIDETECT_DATA_DIR"

# Run application from data directory
cd "$ANTIDETECT_DATA_DIR"
exec /opt/antidetect-browser/AntidetectBrowser "$@"
EOL
chmod 755 "$BUILD_DIR/usr/bin/antidetect-browser"

# Copy .desktop file
cp "$PROJECT_ROOT/build/linux/antidetect-browser.desktop" "$BUILD_DIR/usr/share/applications/"

# Copy icon (use 128x128 for desktop)
if [ -f "$PROJECT_ROOT/build/icons/linux/icon_128x128.png" ]; then
    cp "$PROJECT_ROOT/build/icons/linux/icon_128x128.png" "$BUILD_DIR/usr/share/pixmaps/antidetect-browser.png"
else
    echo "WARNING: Icon not found at build/icons/linux/icon_128x128.png"
fi

# Build .deb package
echo
echo "Building .deb package..."
dpkg-deb --build "$BUILD_DIR"

# Move to dist root
DEB_FILE="${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
mv "${BUILD_DIR}.deb" "$PROJECT_ROOT/dist/$DEB_FILE"

# Clean up build directory
rm -rf "$DEB_DIR"

echo
echo "=== Package created successfully! ==="
echo
echo "Package: dist/$DEB_FILE"
echo "Size: $(du -h "$PROJECT_ROOT/dist/$DEB_FILE" | cut -f1)"
echo
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    INSTALLATION                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo
echo "To install:"
echo "  sudo dpkg -i dist/$DEB_FILE"
echo "  sudo apt-get install -f  # Fix dependencies if needed"
echo
echo "To run:"
echo "  antidetect-browser"
echo
echo "To uninstall:"
echo "  sudo dpkg -r antidetect-browser"
echo
echo "╔════════════════════════════════════════════════════════╗"
echo "║                   USER DATA LOCATION                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo
echo "Profiles and data will be stored in:"
echo "  ~/.local/share/antidetect-browser/data/"
echo
