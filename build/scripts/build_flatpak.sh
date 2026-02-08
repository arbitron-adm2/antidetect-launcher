#!/bin/bash
# Build Flatpak for Antidetect Browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APP_ID="com.antidetect.Browser"
FLATPAK_DIR="$PROJECT_ROOT/build/flatpak"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_flatpak() {
    if ! command -v flatpak &> /dev/null; then
        log_error "Flatpak not installed"
        log_info "Install with: sudo apt-get install flatpak flatpak-builder"
        exit 1
    fi

    # Check if runtime is installed
    if ! flatpak list --runtime | grep -q "org.freedesktop.Platform.*23.08"; then
        log_info "Installing Flatpak runtime..."
        flatpak install -y flathub org.freedesktop.Platform//23.08
        flatpak install -y flathub org.freedesktop.Sdk//23.08
    fi
}

create_manifest() {
    log_info "Creating Flatpak manifest..."

    mkdir -p "$FLATPAK_DIR"

    cat > "$FLATPAK_DIR/$APP_ID.yml" << 'EOF'
app-id: com.antidetect.Browser
runtime: org.freedesktop.Platform
runtime-version: '23.08'
sdk: org.freedesktop.Sdk
command: antidetect-browser
finish-args:
  - --share=ipc
  - --socket=x11
  - --socket=wayland
  - --socket=pulseaudio
  - --share=network
  - --device=dri
  - --filesystem=home
  - --filesystem=xdg-download
  - --talk-name=org.freedesktop.Notifications
  - --talk-name=org.freedesktop.secrets
  - --own-name=com.antidetect.Browser

modules:
  - name: python3
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app --no-cache-dir antidetect-playwright[gui]
    sources:
      - type: archive
        path: ../../dist/antidetect-playwright-0.1.0.tar.gz

  - name: antidetect-browser
    buildsystem: simple
    build-commands:
      - install -Dm755 antidetect-browser.sh /app/bin/antidetect-browser
      - install -Dm644 com.antidetect.Browser.desktop /app/share/applications/com.antidetect.Browser.desktop
      - install -Dm644 icon_256x256.png /app/share/icons/hicolor/256x256/apps/com.antidetect.Browser.png
    sources:
      - type: file
        path: ../../build/linux/antidetect-browser.desktop
        dest-filename: com.antidetect.Browser.desktop
      - type: file
        path: ../../build/icons/linux/icon_256x256.png
      - type: script
        dest-filename: antidetect-browser.sh
        commands:
          - exec python3 -m antidetect_playwright.gui.app "$@"
EOF
}

build_flatpak() {
    log_info "Building Flatpak..."

    cd "$PROJECT_ROOT"

    # Create source distribution
    python3 -m build --sdist

    cd "$FLATPAK_DIR"

    flatpak-builder --force-clean --repo=repo build "$APP_ID.yml"

    # Create bundle
    flatpak build-bundle repo "${APP_ID}-0.1.0.flatpak" "$APP_ID"

    log_info "Flatpak built: $FLATPAK_DIR/${APP_ID}-0.1.0.flatpak"
}

install_flatpak() {
    log_info "Installing Flatpak..."
    flatpak install -y "$FLATPAK_DIR/${APP_ID}-0.1.0.flatpak"
}

# Main
check_flatpak
create_manifest
build_flatpak

log_info "Done! Install with: flatpak install $FLATPAK_DIR/${APP_ID}-0.1.0.flatpak"
log_info "Or run: ./build_flatpak.sh install"
