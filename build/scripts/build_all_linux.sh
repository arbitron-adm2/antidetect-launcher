#!/bin/bash
# Build all Linux package formats
# Usage: ./build_all_linux.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}"
}

# DEB
log_section "Building DEB Package"
"$SCRIPT_DIR/build_deb.sh" build

# AppImage
if command -v wget &> /dev/null; then
    log_section "Building AppImage"
    "$SCRIPT_DIR/build_appimage.sh"
else
    log_info "Skipping AppImage (wget not found)"
fi

# Flatpak
if command -v flatpak &> /dev/null; then
    log_section "Building Flatpak"
    "$SCRIPT_DIR/build_flatpak.sh"
else
    log_info "Skipping Flatpak (flatpak not installed)"
fi

log_section "Build Summary"
echo "DEB: $PROJECT_ROOT/build/debian/antidetect-browser_0.1.0-1_amd64.deb"
[ -f "$PROJECT_ROOT/build/appimage/AntidetectBrowser-0.1.0-x86_64.AppImage" ] && \
    echo "AppImage: $PROJECT_ROOT/build/appimage/AntidetectBrowser-0.1.0-x86_64.AppImage"
[ -f "$PROJECT_ROOT/build/flatpak/com.antidetect.Browser-0.1.0.flatpak" ] && \
    echo "Flatpak: $PROJECT_ROOT/build/flatpak/com.antidetect.Browser-0.1.0.flatpak"

log_info "All builds complete!"
