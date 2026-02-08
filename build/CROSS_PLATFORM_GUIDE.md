# Cross-Platform Packaging Guide

Complete guide for building Antidetect Browser packages across all supported platforms.

## Overview

Antidetect Browser supports three major platforms:
- **Windows**: Inno Setup installer (.exe) + portable ZIP
- **Linux**: DEB package, AppImage, Flatpak
- **macOS**: DMG installer, App bundle

## Platform-Specific Guides

### Windows
See [README_WINDOWS.md](README_WINDOWS.md) for detailed Windows packaging instructions.

**Quick Start:**
```powershell
.\build\build_windows.ps1
```

**Outputs:**
- `AntidetectBrowser-Setup-0.1.0.exe` - Installer
- `AntidetectBrowser-Windows-x64-Portable.zip` - Portable

### Linux

**DEB Package (Ubuntu/Debian):**
```bash
./build/scripts/build_deb.sh build
```

**AppImage (Universal):**
```bash
./build/scripts/build_appimage.sh
```

**Flatpak:**
```bash
./build/scripts/build_flatpak.sh
```

### macOS

**DMG Installer:**
```bash
./build/scripts/build_dmg.sh
```

## Common Build Steps

All platforms follow a similar build process:

### 1. Prerequisites

**All Platforms:**
- Python 3.12+
- Git
- PyInstaller 6.11+

**Platform-Specific:**
- Windows: Inno Setup 6, Windows SDK (for signing)
- Linux: dpkg-dev, fakeroot, desktop-file-utils
- macOS: create-dmg, Xcode Command Line Tools

### 2. Install Dependencies

```bash
# All platforms
pip install -e ".[gui,package]"
```

### 3. Generate Icons

```bash
python build/generate_icons.py
```

This creates platform-specific icons:
- Windows: `icon.ico`
- Linux: `icon_*.png` (multiple sizes)
- macOS: `icon.icns`

### 4. Build with PyInstaller

```bash
pyinstaller antidetect-browser.spec --clean --noconfirm
```

### 5. Create Platform Package

Use platform-specific scripts (see above).

## Cross-Platform Considerations

### File Paths
- **Windows**: Use backslashes or `Path()` objects
- **Linux/macOS**: Forward slashes
- **Recommended**: Use `pathlib.Path()` for all path operations

### Icons
- **Windows**: Single `.ico` file with multiple sizes embedded
- **Linux**: PNG files in standard sizes (16, 24, 32, 48, 64, 128, 256)
- **macOS**: `.icns` with standard iconset sizes

### Desktop Integration

**Windows:**
- Start Menu shortcuts
- Desktop icon (optional)
- Registry entries for settings
- File associations

**Linux:**
- `.desktop` file in `/usr/share/applications/`
- Icons in `/usr/share/icons/hicolor/*/apps/`
- MIME type associations

**macOS:**
- App bundle structure
- Info.plist configuration
- LaunchServices integration

### Executable Naming
- **Windows**: `AntidetectBrowser.exe`
- **Linux**: `antidetect-browser` (lowercase, hyphenated)
- **macOS**: `Antidetect Browser.app` (bundle)

### Permissions

**Windows:**
- User-level install (no admin) by default
- UAC manifest included
- Installer can elevate if needed

**Linux:**
- Standard executable permissions (755)
- Desktop file permissions (644)
- Installed to system paths require sudo

**macOS:**
- Gatekeeper-compatible signing required
- Notarization for distribution
- App bundle permissions

## Version Management

Update version in these files:
1. `pyproject.toml` - Package version
2. `build/version_info.txt` - Windows PE version
3. `build/installer.iss` - Inno Setup version
4. `debian/changelog` - DEB package version
5. `src/antidetect_playwright/gui/updater.py` - Auto-update version

**Recommended:** Use `bump2version` or similar tool to update all at once.

## Code Signing

### Windows
```powershell
.\build\build_windows.ps1 -Sign -SignCert "cert.pfx" -SignPassword "pass"
```

Requirements:
- Code signing certificate (.pfx)
- Windows SDK (signtool.exe)
- Timestamp server

### macOS
```bash
codesign --sign "Developer ID Application: Your Name" \
         --timestamp \
         --options runtime \
         dist/AntidetectBrowser.app
```

Requirements:
- Apple Developer ID certificate
- Xcode Command Line Tools
- Notarization for public distribution

### Linux
```bash
debsign -k YOUR_GPG_KEY package.deb
```

Requirements:
- GPG key for signing
- Optional for most distributions

## CI/CD Integration

### GitHub Actions Workflows

**Windows Build:**
```yaml
- uses: ./.github/workflows/build-windows.yml
```

**Linux Build:**
```yaml
- uses: ./.github/workflows/build-linux.yml
```

**Full Release:**
```yaml
- uses: ./.github/workflows/build.yml
```

### Automated Builds

Builds are triggered on:
- Push to `main` or `develop` branches
- Pull requests
- Version tags (`v*.*.*`)
- Manual workflow dispatch

### Artifacts

Each platform uploads:
- Installer/package files
- Portable/archive versions
- Checksums (SHA256)
- Build logs (on failure)

## Testing

### Windows
```powershell
# Install silently
.\AntidetectBrowser-Setup-0.1.0.exe /VERYSILENT

# Verify installation
Test-Path "$env:ProgramFiles\Antidetect Browser\AntidetectBrowser.exe"

# Uninstall
& "$env:ProgramFiles\Antidetect Browser\unins000.exe" /VERYSILENT
```

### Linux (DEB)
```bash
# Install
sudo dpkg -i antidetect-browser_0.1.0-1_amd64.deb

# Verify
which antidetect-browser
antidetect-browser --version

# Uninstall
sudo apt remove antidetect-browser
```

### macOS
```bash
# Mount DMG
hdiutil attach AntidetectBrowser-0.1.0.dmg

# Copy to Applications
cp -R "/Volumes/Antidetect Browser/Antidetect Browser.app" /Applications/

# Eject
hdiutil detach "/Volumes/Antidetect Browser"
```

## Distribution Channels

### Windows
- GitHub Releases
- Microsoft Store (future)
- Winget package manager (future)

### Linux
- GitHub Releases
- APT repository (custom)
- Flathub (Flatpak)
- Snap Store (future)

### macOS
- GitHub Releases
- Homebrew Cask (future)
- Mac App Store (future)

## Build Matrix

| Platform | Format | Auto-Update | Code Sign | Size |
|----------|--------|-------------|-----------|------|
| Windows  | EXE    | ✅          | Optional  | ~150MB |
| Windows  | ZIP    | ❌          | N/A       | ~140MB |
| Linux    | DEB    | ❌          | Optional  | ~130MB |
| Linux    | AppImage | ✅       | Optional  | ~140MB |
| Linux    | Flatpak | ✅        | ❌        | ~150MB |
| macOS    | DMG    | ✅          | Required  | ~160MB |

## Troubleshooting

### Build Failures

**Windows:**
- Ensure Inno Setup is installed
- Check icon files exist in `build/icons/`
- Verify all dependencies installed

**Linux:**
- Install build dependencies: `sudo apt install devscripts debhelper`
- Check debian/ directory exists
- Verify desktop file is valid

**macOS:**
- Install create-dmg: `brew install create-dmg`
- Ensure iconset is valid
- Check Info.plist syntax

### Size Optimization

**Reduce package size:**
1. Enable UPX compression in spec file
2. Exclude unnecessary modules (matplotlib, scipy, etc.)
3. Strip debug symbols
4. Compress resources

**Example:**
```python
# In antidetect-browser.spec
upx=True,
excludes=['matplotlib', 'pandas', 'scipy'],
strip=True,
```

### Platform-Specific Issues

**Windows - DLL Hell:**
- Use `--clean` flag with PyInstaller
- Check for conflicting DLL versions
- Use dependency walker to analyze

**Linux - Missing Libraries:**
- Include required libs in package
- Use `ldd` to check dependencies
- Consider static linking for problematic libs

**macOS - Gatekeeper:**
- Sign with valid Developer ID
- Notarize the app
- Use `spctl` to verify signature

## Best Practices

### Version Numbering
Use semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Release Process
1. Update version in all files
2. Update CHANGELOG
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push --tags`
5. CI/CD builds and creates release
6. Test installers on clean systems
7. Announce release

### Changelog
Maintain CHANGELOG.md with:
- Added features
- Changed functionality
- Deprecated features
- Removed features
- Fixed bugs
- Security patches

### Security
- Sign all production builds
- Use HTTPS for downloads
- Verify checksums
- Keep dependencies updated
- Scan for vulnerabilities

## Resources

**Windows:**
- Inno Setup: https://jrsoftware.org/isinfo.php
- PyInstaller Windows: https://pyinstaller.org/en/stable/operating-mode.html#windows

**Linux:**
- Debian Packaging: https://www.debian.org/doc/manuals/maint-guide/
- AppImage: https://appimage.org/
- Flatpak: https://flatpak.org/

**macOS:**
- create-dmg: https://github.com/sindresorhus/create-dmg
- Notarization: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution

**General:**
- PyInstaller: https://pyinstaller.org/
- Python Packaging: https://packaging.python.org/

## Support

For platform-specific build issues:
- Windows: See `build/README_WINDOWS.md`
- Linux: Check `build/scripts/build_*.sh`
- General: Open issue on GitHub
