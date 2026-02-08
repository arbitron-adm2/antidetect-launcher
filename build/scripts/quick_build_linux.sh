#!/bin/bash
# Quick DEB build for development
# Skips validation and tests for rapid iteration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "  Quick DEB Build (Development Mode)"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

# Clean previous build artifacts
echo "Cleaning previous builds..."
rm -rf debian/.debhelper debian/antidetect-browser debian/tmp
rm -f debian/files debian/*.log debian/*.substvars
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Building DEB package (quick mode)..."

# Build with minimal checks
# -us -uc: Don't sign
# -b: Binary only
# -d: Don't check build dependencies
# --no-check-builddeps: Skip dependency checks
dpkg-buildpackage -us -uc -b -d --no-check-builddeps 2>&1 | grep -E "dpkg-deb|dpkg-buildpackage" || true

# Move to build directory
mkdir -p build/debian
mv ../*.deb build/debian/ 2>/dev/null || true
mv ../*.changes build/debian/ 2>/dev/null || true
mv ../*.buildinfo build/debian/ 2>/dev/null || true

echo ""
echo "=========================================="
echo "  Quick Build Complete!"
echo "=========================================="
echo ""

# Find the .deb file
DEB_FILE=$(find build/debian -name "*.deb" -type f | head -1)

if [ -n "$DEB_FILE" ]; then
    echo "Package: $DEB_FILE"
    echo "Size: $(du -h "$DEB_FILE" | cut -f1)"
    echo ""
    echo "Install with:"
    echo "  sudo dpkg -i $DEB_FILE"
    echo "  sudo apt-get install -f  # Fix dependencies if needed"
else
    echo "Warning: .deb file not found"
    exit 1
fi

echo ""
echo "Note: This is a development build without full validation."
echo "For production builds, use: ./build/scripts/build_deb.sh"
