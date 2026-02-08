#!/bin/bash
# Local build script for all platforms
# Builds executable/package for current platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════╗"
echo "║         Antidetect Browser - Local Build              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
else
    echo "ERROR: Unsupported platform: $OSTYPE"
    exit 1
fi

echo "Platform detected: $PLATFORM"
echo

# Parse arguments
BUILD_TYPE="all"
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --exe|--executable)
            BUILD_TYPE="exe"
            shift
            ;;
        --package)
            BUILD_TYPE="package"
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--exe|--package|--clean]"
            exit 1
            ;;
    esac
done

# Clean build
if [ "$CLEAN" = true ]; then
    echo "Cleaning previous builds..."
    rm -rf build/ dist/ *.spec
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    echo
fi

# Build executable
if [ "$BUILD_TYPE" = "all" ] || [ "$BUILD_TYPE" = "exe" ]; then
    echo "=== Building executable ==="
    echo
    chmod +x "$SCRIPT_DIR/build.sh"
    "$SCRIPT_DIR/build.sh"
    echo
fi

# Build platform package
if [ "$BUILD_TYPE" = "all" ] || [ "$BUILD_TYPE" = "package" ]; then
    echo "=== Building platform package ==="
    echo

    case $PLATFORM in
        linux)
            chmod +x "$SCRIPT_DIR/build_deb.sh"
            "$SCRIPT_DIR/build_deb.sh"
            ;;
        macos)
            chmod +x "$SCRIPT_DIR/build_dmg.sh"
            "$SCRIPT_DIR/build_dmg.sh"
            ;;
        windows)
            python "$SCRIPT_DIR/build_installer.py"
            ;;
    esac
    echo
fi

echo "╔════════════════════════════════════════════════════════╗"
echo "║                 Build Complete!                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo
echo "Build artifacts are in: dist/"
ls -lh dist/ 2>/dev/null || dir dist\ 2>/dev/null || true
echo
