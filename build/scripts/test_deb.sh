#!/bin/bash
# Test DEB package installation and functionality

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DEB_FILE="$1"
PASSED=0
FAILED=0

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

if [ -z "$DEB_FILE" ]; then
    echo "Usage: $0 <path-to-deb-file>"
    exit 1
fi

if [ ! -f "$DEB_FILE" ]; then
    log_fail "DEB file not found: $DEB_FILE"
    exit 1
fi

log_info "Testing DEB package: $DEB_FILE"

# Test 1: Package info
log_info "Test 1: Checking package metadata..."
if dpkg-deb --info "$DEB_FILE" | grep -q "antidetect-browser"; then
    log_pass "Package metadata is valid"
else
    log_fail "Package metadata is invalid"
fi

# Test 2: Package contents
log_info "Test 2: Checking package contents..."
if dpkg-deb --contents "$DEB_FILE" | grep -q "usr/bin/antidetect-browser"; then
    log_pass "Package contains expected files"
else
    log_fail "Package missing expected files"
fi

# Test 3: Desktop file
if dpkg-deb --contents "$DEB_FILE" | grep -q "applications/antidetect-browser.desktop"; then
    log_pass "Desktop file present"
else
    log_fail "Desktop file missing"
fi

# Test 4: Icons
if dpkg-deb --contents "$DEB_FILE" | grep -q "hicolor.*antidetect-browser.png"; then
    log_pass "Icons present"
else
    log_fail "Icons missing"
fi

# Test 5: Lintian
log_info "Test 5: Running lintian..."
if lintian "$DEB_FILE" 2>&1 | grep -qE "E:|F:"; then
    log_fail "Lintian found errors"
    lintian "$DEB_FILE" | grep -E "E:|F:" || true
else
    log_pass "Lintian check passed (no errors)"
fi

# Summary
echo ""
log_info "========================================="
log_info "Test Summary"
log_info "========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    log_pass "All tests passed!"
    exit 0
else
    log_fail "Some tests failed"
    exit 1
fi
