#!/bin/bash
# Build standalone executable for current platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Antidetect Browser Build Script ==="
echo

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found."
    echo "Run ./setup.sh first."
    exit 1
fi

# Activate venv
echo "Activating virtual environment..."
source .venv/bin/activate

# Install package dependencies
echo "Installing package dependencies..."
pip install -e ".[gui,package]"

# Generate icons
echo
echo "Generating application icons..."
python scripts/generate_icons.py

# Build with PyInstaller
echo
echo "Building executable with PyInstaller..."
pyinstaller antidetect-browser.spec --clean --noconfirm

# Check result
if [ -d "dist/AntidetectBrowser" ]; then
    echo
    echo "=== Build successful! ==="
    echo
    echo "Executable location:"
    if [ "$(uname)" == "Darwin" ]; then
        echo "  dist/AntidetectBrowser.app"
        echo
        echo "To run:"
        echo "  open dist/AntidetectBrowser.app"
    else
        echo "  dist/AntidetectBrowser/AntidetectBrowser"
        echo
        echo "To run:"
        echo "  ./dist/AntidetectBrowser/AntidetectBrowser"
    fi
    echo
    echo "To create distributable archive:"
    echo "  cd dist && tar -czf AntidetectBrowser-$(uname -s)-$(uname -m).tar.gz AntidetectBrowser"
else
    echo
    echo "ERROR: Build failed. Check output above."
    exit 1
fi
