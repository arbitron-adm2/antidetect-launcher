#!/bin/bash
# Fix missing glxtest/vaapitest for Camoufox on Linux
# These files are needed for GPU detection and hardware acceleration

CAMOUFOX_DIR="$HOME/.cache/camoufox"
FIREFOX_DIR="/usr/lib/firefox"

echo "Fixing Camoufox GPU detection files..."

# Copy glxtest if missing
if [ ! -f "$CAMOUFOX_DIR/glxtest" ] && [ -f "$FIREFOX_DIR/glxtest" ]; then
    cp "$FIREFOX_DIR/glxtest" "$CAMOUFOX_DIR/glxtest"
    chmod +x "$CAMOUFOX_DIR/glxtest"
    echo "✓ Copied glxtest"
else
    if [ -f "$CAMOUFOX_DIR/glxtest" ]; then
        echo "✓ glxtest already exists"
    else
        echo "✗ glxtest not found in Firefox installation"
    fi
fi

# Copy vaapitest if missing (for video acceleration)
if [ ! -f "$CAMOUFOX_DIR/vaapitest" ] && [ -f "$FIREFOX_DIR/vaapitest" ]; then
    cp "$FIREFOX_DIR/vaapitest" "$CAMOUFOX_DIR/vaapitest"
    chmod +x "$CAMOUFOX_DIR/vaapitest"
    echo "✓ Copied vaapitest"
else
    if [ -f "$CAMOUFOX_DIR/vaapitest" ]; then
        echo "✓ vaapitest already exists"
    else
        echo "✗ vaapitest not found in Firefox installation"
    fi
fi

echo "Done! GPU acceleration should now work properly."
