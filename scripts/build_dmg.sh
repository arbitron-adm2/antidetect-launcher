#!/bin/bash
# Build macOS .dmg installer
# This script creates a distributable DMG for macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
APP_NAME="AntidetectBrowser"
DMG_NAME="AntidetectBrowser-macOS-${VERSION}.dmg"

cd "$PROJECT_ROOT"

echo "=== Creating macOS DMG installer ==="
echo "Version: $VERSION"
echo

# Check if .app exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "ERROR: dist/${APP_NAME}.app not found!"
    echo "Run ./scripts/build.sh first to build the application."
    exit 1
fi

# Create temporary directory for DMG contents
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo "Preparing DMG contents..."
cp -R "dist/${APP_NAME}.app" "$TMP_DIR/"

# Create Applications symlink
ln -s /Applications "$TMP_DIR/Applications"

# Create DMG background directory (optional)
# mkdir -p "$TMP_DIR/.background"
# cp "build/macos/dmg-background.png" "$TMP_DIR/.background/" || true

echo "Creating DMG..."

# Remove old DMG if exists
rm -f "dist/$DMG_NAME"

# Create DMG using hdiutil
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$TMP_DIR" \
    -ov -format UDZO \
    "dist/$DMG_NAME"

echo
echo "=== DMG created successfully! ==="
echo
echo "DMG: dist/$DMG_NAME"
echo "Size: $(du -h "dist/$DMG_NAME" | cut -f1)"
echo
echo "To install:"
echo "  1. Open dist/$DMG_NAME"
echo "  2. Drag AntidetectBrowser.app to Applications folder"
echo
