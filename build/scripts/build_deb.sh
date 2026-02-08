#!/bin/bash
# Build .deb package for Antidetect Browser
# Usage: ./build_deb.sh [clean|build|install]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGE_NAME="antidetect-browser"
VERSION="0.1.0"
ARCH="amd64"
BUILD_DIR="$PROJECT_ROOT/build/debian"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking build dependencies..."

    local missing_deps=()

    # Check for required tools
    for cmd in dpkg-buildpackage debuild dh_make lintian; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Install with: sudo apt-get install devscripts debhelper dh-python build-essential"
        exit 1
    fi

    # Check Python version
    if ! python3 --version | grep -q "Python 3.12"; then
        log_warn "Python 3.12 is recommended but not found"
        log_warn "Current version: $(python3 --version)"
    fi

    log_info "All dependencies satisfied"
}

clean_build() {
    log_info "Cleaning previous build artifacts..."

    cd "$PROJECT_ROOT"

    # Clean debian build artifacts
    rm -rf debian/.debhelper
    rm -rf debian/antidetect-browser
    rm -rf debian/tmp
    rm -f debian/files
    rm -f debian/*.log
    rm -f debian/*.substvars
    rm -f debian/*.debhelper

    # Clean Python artifacts
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

    # Clean build directory
    rm -rf "$BUILD_DIR"
    rm -rf build/dist
    rm -f ../${PACKAGE_NAME}_*.deb
    rm -f ../${PACKAGE_NAME}_*.changes
    rm -f ../${PACKAGE_NAME}_*.buildinfo
    rm -f ../${PACKAGE_NAME}_*.tar.xz
    rm -f ../${PACKAGE_NAME}_*.dsc

    log_info "Clean complete"
}

build_package() {
    log_info "Building .deb package..."

    cd "$PROJECT_ROOT"

    # Ensure debian directory exists
    if [ ! -d "debian" ]; then
        log_error "debian/ directory not found!"
        exit 1
    fi

    # Make maintainer scripts executable
    chmod +x debian/rules
    chmod +x debian/postinst debian/prerm debian/postrm 2>/dev/null || true

    # Build the package
    log_info "Running dpkg-buildpackage..."
    dpkg-buildpackage -us -uc -b --jobs=auto

    # Move the .deb to build directory
    mkdir -p "$BUILD_DIR"
    mv ../${PACKAGE_NAME}_*.deb "$BUILD_DIR/" 2>/dev/null || true
    mv ../${PACKAGE_NAME}_*.changes "$BUILD_DIR/" 2>/dev/null || true
    mv ../${PACKAGE_NAME}_*.buildinfo "$BUILD_DIR/" 2>/dev/null || true

    log_info "Package built successfully!"
    log_info "Location: $BUILD_DIR/${PACKAGE_NAME}_${VERSION}-1_${ARCH}.deb"

    # Run lintian checks
    log_info "Running lintian checks..."
    lintian "$BUILD_DIR/${PACKAGE_NAME}_${VERSION}-1_${ARCH}.deb" || {
        log_warn "Lintian found some issues (non-fatal)"
    }
}

install_package() {
    log_info "Installing package..."

    local deb_file="$BUILD_DIR/${PACKAGE_NAME}_${VERSION}-1_${ARCH}.deb"

    if [ ! -f "$deb_file" ]; then
        log_error "Package file not found: $deb_file"
        log_info "Run './build_deb.sh build' first"
        exit 1
    fi

    sudo dpkg -i "$deb_file" || {
        log_warn "Dependency issues detected, fixing..."
        sudo apt-get install -f -y
    }

    log_info "Package installed successfully!"
    log_info "Run 'antidetect-browser' to launch the application"
}

show_info() {
    log_info "Package information:"
    local deb_file="$BUILD_DIR/${PACKAGE_NAME}_${VERSION}-1_${ARCH}.deb"

    if [ -f "$deb_file" ]; then
        dpkg-deb --info "$deb_file"
        echo ""
        log_info "Package contents:"
        dpkg-deb --contents "$deb_file" | head -20
    else
        log_error "Package not found. Build it first."
    fi
}

show_usage() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    clean       Clean build artifacts
    build       Build .deb package
    install     Install the built package
    info        Show package information
    all         Clean, build, and show info
    help        Show this help message

Examples:
    $0 clean
    $0 build
    $0 all
    $0 install

EOF
}

# Main
case "${1:-build}" in
    clean)
        clean_build
        ;;
    build)
        check_dependencies
        clean_build
        build_package
        ;;
    install)
        install_package
        ;;
    info)
        show_info
        ;;
    all)
        check_dependencies
        clean_build
        build_package
        show_info
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

exit 0
