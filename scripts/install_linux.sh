#!/bin/bash
# Install Antidetect Browser on Linux (system-wide or user)

set -e

INSTALL_TYPE="${1:-user}"  # 'user' or 'system'

if [ "$INSTALL_TYPE" = "system" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "ERROR: System-wide installation requires root."
        echo "Run: sudo $0 system"
        exit 1
    fi
    BIN_DIR="/usr/local/bin"
    ICON_DIR="/usr/share/icons/hicolor"
    DESKTOP_DIR="/usr/share/applications"
else
    BIN_DIR="$HOME/.local/bin"
    ICON_DIR="$HOME/.local/share/icons/hicolor"
    DESKTOP_DIR="$HOME/.local/share/applications"
fi

echo "=== Antidetect Browser Installation ==="
echo "Install type: $INSTALL_TYPE"
echo

# Create directories
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# Install icons
echo "Installing icons..."
for size in 16 24 32 48 64 128 256 512; do
    ICON_SIZE_DIR="$ICON_DIR/${size}x${size}/apps"
    mkdir -p "$ICON_SIZE_DIR"
    
    if [ -f "build/icons/linux/icon_${size}x${size}.png" ]; then
        cp "build/icons/linux/icon_${size}x${size}.png" "$ICON_SIZE_DIR/antidetect-browser.png"
    fi
done

# Update icon cache (if available)
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
fi

# Install desktop entry
echo "Installing desktop entry..."
DESKTOP_FILE="$DESKTOP_DIR/antidetect-browser.desktop"

# Get actual installation path of antidetect-browser command
VENV_PATH="$(pwd)/.venv"
if [ -f "$VENV_PATH/bin/antidetect-browser" ]; then
    EXEC_PATH="$VENV_PATH/bin/antidetect-browser"
else
    EXEC_PATH="antidetect-browser"
fi

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Antidetect Browser
GenericName=Anti-Detection Browser Manager
Comment=Manage browser profiles with fingerprint spoofing
Exec=$EXEC_PATH
Icon=antidetect-browser
Terminal=false
Categories=Network;WebBrowser;Development;
Keywords=browser;antidetect;fingerprint;automation;privacy;
StartupNotify=true
StartupWMClass=antidetect-browser
Path=$(pwd)
EOF

chmod +x "$DESKTOP_FILE"

# Update desktop database (if available)
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo
echo "=== Installation complete! ==="
echo
echo "You can now launch Antidetect Browser from:"
echo "  - Application menu (search for 'Antidetect Browser')"
echo "  - Command line: $EXEC_PATH"
echo
