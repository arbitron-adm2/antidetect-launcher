#!/bin/bash
# Build script for Antidetect Browser based on Camoufox

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
CAMOUFOX_DIR="$BUILD_DIR/../camoufox"
OUTPUT_DIR="$BUILD_DIR/output"

BRAND_NAME="Antidetect Browser"
BRAND_SHORT="antidetect"

echo "=== Antidetect Browser Build Script ==="
echo "Build dir: $BUILD_DIR"
echo "Camoufox dir: $CAMOUFOX_DIR"

# Check camoufox exists
if [ ! -d "$CAMOUFOX_DIR" ]; then
    echo "ERROR: Camoufox directory not found at $CAMOUFOX_DIR"
    exit 1
fi

# Find source directory
MOZILLA_DIR=$(find "$CAMOUFOX_DIR" -maxdepth 1 -type d -name "camoufox-*" | head -1)
if [ -z "$MOZILLA_DIR" ]; then
    echo "ERROR: Camoufox source not found. Run 'make fetch' in camoufox first."
    exit 1
fi

echo "Mozilla source: $MOZILLA_DIR"

# Step 1: Create branding directory
echo ""
echo "=== Step 1: Setting up branding ==="

BRANDING_DIR="$MOZILLA_DIR/browser/branding/$BRAND_SHORT"
mkdir -p "$BRANDING_DIR"

# Copy branding from Camoufox as base
if [ -d "$CAMOUFOX_DIR/additions/browser/branding/camoufox" ]; then
    cp -r "$CAMOUFOX_DIR/additions/browser/branding/camoufox/"* "$BRANDING_DIR/"
fi

# Generate PNG icons from SVG
if command -v rsvg-convert &> /dev/null; then
    echo "Generating icons from SVG..."
    for size in 16 22 24 32 48 64 128 256; do
        rsvg-convert -w $size -h $size "$BUILD_DIR/branding/icon.svg" -o "$BRANDING_DIR/default${size}.png"
    done
    # Also create logo.png
    rsvg-convert -w 256 -h 256 "$BUILD_DIR/branding/icon.svg" -o "$BRANDING_DIR/logo.png"
elif command -v convert &> /dev/null; then
    echo "Generating icons using ImageMagick..."
    for size in 16 22 24 32 48 64 128 256; do
        convert -background none -resize ${size}x${size} "$BUILD_DIR/branding/icon.svg" "$BRANDING_DIR/default${size}.png"
    done
    convert -background none -resize 256x256 "$BUILD_DIR/branding/icon.svg" "$BRANDING_DIR/logo.png"
else
    echo "WARNING: No SVG converter found. Using existing icons."
fi

# Update branding strings
echo "Updating branding strings..."
cat > "$BRANDING_DIR/locales/en-US/brand.dtd" << 'EOF'
<!ENTITY  brandShortName        "Antidetect Browser">
<!ENTITY  brandShorterName      "Antidetect">
<!ENTITY  brandFullName         "Antidetect Browser">
<!ENTITY  vendorShortName       "Antidetect">
<!ENTITY  trademarkInfo.part1   "">
EOF

cat > "$BRANDING_DIR/locales/en-US/brand.ftl" << 'EOF'
-brand-shorter-name = Antidetect
-brand-short-name = Antidetect Browser
-brand-full-name = Antidetect Browser
-vendor-short-name = Antidetect
trademarks = 
EOF

cat > "$BRANDING_DIR/locales/en-US/brand.properties" << 'EOF'
brandShortName=Antidetect Browser
brandShorterName=Antidetect
brandFullName=Antidetect Browser
vendorShortName=Antidetect
homePageSingleStartMain=
homePageImport=
homePageMigrationPageTitle=
homePageMigrationDescription=
EOF

# Step 2: Setup chrome styles (Lepton)
echo ""
echo "=== Step 2: Setting up Lepton styles ==="

LW_DIR="$MOZILLA_DIR/lw"
mkdir -p "$LW_DIR"

# Copy Lepton chrome styles
if [ -d "$BUILD_DIR/chrome" ]; then
    cp -r "$BUILD_DIR/chrome/"* "$LW_DIR/"
    echo "Copied Lepton styles to $LW_DIR"
fi

# Create/update camoufox.cfg with Lepton prefs
cat > "$LW_DIR/camoufox.cfg" << 'EOF'
// Camoufox + Antidetect Browser config

// Enable userChrome.css
pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Lepton required prefs
pref("svg.context-properties.content.enabled", true);
pref("browser.compactmode.show", true);
pref("layout.css.has-selector.enabled", true);

// Lepton theme settings
pref("userChrome.tab.connect_to_window", true);
pref("userChrome.tab.color_like_toolbar", true);
pref("userChrome.tab.lepton_like_padding", true);
pref("userChrome.tab.photon_like_padding", false);
pref("userChrome.tab.dynamic_separator", true);
pref("userChrome.tab.static_separator", false);
pref("userChrome.tab.newtab_button_like_tab", true);
pref("userChrome.tab.box_shadow", true);
pref("userChrome.tab.bottom_rounded_corner", true);
pref("userChrome.icon.panel_full", true);
pref("userChrome.icon.panel_photon", false);

// UI improvements
pref("browser.tabs.tabClipWidth", 83);
pref("security.insecure_connection_text.enabled", true);
pref("browser.newtabpage.activity-stream.improvesearch.handoffToAwesomebar", false);
EOF

# Step 3: Create mozconfig
echo ""
echo "=== Step 3: Creating mozconfig ==="

cat > "$MOZILLA_DIR/.mozconfig" << EOF
# Antidetect Browser mozconfig

ac_add_options --enable-application=browser
 
ac_add_options --allow-addon-sideload
ac_add_options --disable-crashreporter
ac_add_options --disable-backgroundtasks
ac_add_options --disable-debug
ac_add_options --disable-default-browser-agent
ac_add_options --disable-tests
ac_add_options --disable-updater
ac_add_options --enable-release
ac_add_options --enable-optimize

ac_add_options --disable-system-policies

# Antidetect Browser branding
ac_add_options --with-app-name=$BRAND_SHORT
ac_add_options --with-branding=browser/branding/$BRAND_SHORT

ac_add_options --with-unsigned-addon-scopes=app,system

ac_add_options --enable-bootstrap

export MOZ_REQUIRE_SIGNING=

mk_add_options MOZ_CRASHREPORTER=0
mk_add_options MOZ_DATA_REPORTING=0
mk_add_options MOZ_SERVICES_HEALTHREPORT=0
mk_add_options MOZ_TELEMETRY_REPORTING=0
mk_add_options MOZ_INSTALLER=0
mk_add_options MOZ_AUTOMATION_INSTALLER=0

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-\$(uname -m)-pc-linux-gnu
EOF

# Step 4: Update moz.build for branding
echo ""
echo "=== Step 4: Updating moz.build ==="

BRANDING_MOZ_BUILD="$BRANDING_DIR/moz.build"
if [ ! -f "$BRANDING_MOZ_BUILD" ]; then
    cat > "$BRANDING_MOZ_BUILD" << 'EOF'
# -*- Mode: python; indent-tabs-mode: nil; tab-width: 40 -*-
# vim: set filetype=python:

DIRS += ["content", "locales"]

FINAL_TARGET_FILES.chrome.icons.default += [
    "default16.png",
    "default32.png",
    "default48.png",
    "default64.png",
    "default128.png",
]
EOF
fi

echo ""
echo "=== Build preparation complete ==="
echo ""
echo "To build the browser, run:"
echo "  cd $MOZILLA_DIR"
echo "  ./mach build"
echo ""
echo "Or run this script with --build flag to start build now."

if [ "$1" == "--build" ]; then
    echo ""
    echo "=== Starting build ==="
    cd "$MOZILLA_DIR"
    ./mach build
    
    echo ""
    echo "=== Build complete ==="
    echo "Browser executable: $MOZILLA_DIR/obj-*/dist/bin/$BRAND_SHORT"
fi
