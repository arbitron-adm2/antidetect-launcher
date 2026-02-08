#!/bin/bash
# Build AppImage for Antidetect Browser
# Requires: appimagetool, linuxdeploy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APP_NAME="AntidetectBrowser"
VERSION="0.1.0"
APPDIR="$PROJECT_ROOT/build/appimage/AppDir"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_tools() {
    log_info "Checking required tools..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi

    # Download appimagetool if not present
    if ! command -v appimagetool &> /dev/null; then
        log_info "Downloading appimagetool..."
        wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
            -O /tmp/appimagetool
        chmod +x /tmp/appimagetool
        APPIMAGETOOL="/tmp/appimagetool"
    else
        APPIMAGETOOL="appimagetool"
    fi
}

prepare_appdir() {
    log_info "Preparing AppDir..."

    rm -rf "$APPDIR"
    mkdir -p "$APPDIR"

    # Create directory structure
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/lib"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

    # Create Python virtual environment
    python3 -m venv "$APPDIR/usr/venv"

    # Install application
    "$APPDIR/usr/venv/bin/pip" install --no-cache-dir --upgrade pip
    "$APPDIR/usr/venv/bin/pip" install --no-cache-dir "$PROJECT_ROOT"
    "$APPDIR/usr/venv/bin/pip" install --no-cache-dir "$PROJECT_ROOT[gui]"

    # Install Playwright
    "$APPDIR/usr/venv/bin/playwright" install chromium

    # Copy icon
    cp "$PROJECT_ROOT/build/icons/linux/icon_256x256.png" \
        "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"

    # Create AppRun script
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF_DIR="$(dirname "$(readlink -f "$0")")"
export PATH="$SELF_DIR/usr/venv/bin:$PATH"
export PYTHONHOME="$SELF_DIR/usr/venv"
export PYTHONPATH="$SELF_DIR/usr/venv/lib/python3.12/site-packages"
exec "$SELF_DIR/usr/venv/bin/python3" -m antidetect_playwright.gui.app "$@"
EOF
    chmod +x "$APPDIR/AppRun"

    # Create desktop file
    cat > "$APPDIR/$APP_NAME.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Antidetect Browser
Comment=Anti-Detection Browser Manager
Exec=AppRun
Icon=$APP_NAME
Categories=Network;WebBrowser;Development;
Terminal=false
EOF

    cp "$APPDIR/$APP_NAME.desktop" "$APPDIR/usr/share/applications/"

    # Copy icon to root
    cp "$PROJECT_ROOT/build/icons/linux/icon_256x256.png" "$APPDIR/$APP_NAME.png"

    log_info "AppDir prepared"
}

build_appimage() {
    log_info "Building AppImage..."

    cd "$PROJECT_ROOT/build/appimage"

    ARCH=x86_64 $APPIMAGETOOL "$APPDIR" "${APP_NAME}-${VERSION}-x86_64.AppImage"

    log_info "AppImage built: $PROJECT_ROOT/build/appimage/${APP_NAME}-${VERSION}-x86_64.AppImage"
}

# Main
check_tools
prepare_appdir
build_appimage

log_info "Done! Run the AppImage with: ./build/appimage/${APP_NAME}-${VERSION}-x86_64.AppImage"
