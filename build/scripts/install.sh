#!/bin/bash
# Install script: creates symlink and updates config for Antidetect Browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$BUILD_DIR")"
CAMOUFOX_DIR="$BUILD_DIR/../camoufox"

# Find Mozilla source directory
MOZILLA_DIR=$(find "$CAMOUFOX_DIR" -maxdepth 1 -type d -name "camoufox-*" | head -1)
if [ -z "$MOZILLA_DIR" ]; then
    echo "ERROR: Camoufox source not found"
    exit 1
fi

# Find built browser
BROWSER_PATH="$MOZILLA_DIR/obj-x86_64-pc-linux-gnu/dist/bin/antidetect"
if [ ! -f "$BROWSER_PATH" ]; then
    echo "ERROR: Built browser not found at $BROWSER_PATH"
    echo "Make sure the build has completed successfully."
    exit 1
fi

echo "Found built browser: $BROWSER_PATH"

# Create output directory with symlink
OUTPUT_DIR="$BUILD_DIR/output"
mkdir -p "$OUTPUT_DIR"

# Create symlink to built browser
ln -sf "$BROWSER_PATH" "$OUTPUT_DIR/antidetect"
echo "Created symlink: $OUTPUT_DIR/antidetect -> $BROWSER_PATH"

# Copy required Camoufox files
cp "$PROJECT_DIR/camoufox/settings/properties.json" "$OUTPUT_DIR/"
echo "Copied properties.json for Camoufox compatibility"

# Update settings.json with browser path
SETTINGS_FILE="$PROJECT_DIR/data/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # Use python to update JSON properly
    python3 << PYEOF
import json
settings_path = "$SETTINGS_FILE"
browser_path = "$OUTPUT_DIR/antidetect"

with open(settings_path, 'r') as f:
    settings = json.load(f)

settings['browser_executable_path'] = browser_path

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print(f"Updated {settings_path}")
print(f"browser_executable_path = {browser_path}")
PYEOF
else
    echo "WARNING: settings.json not found at $SETTINGS_FILE"
fi

echo ""
echo "=== Installation complete! ==="
echo "Browser path: $OUTPUT_DIR/antidetect"
echo ""
echo "You can now run the Antidetect Playwright GUI and it will use the custom browser."
