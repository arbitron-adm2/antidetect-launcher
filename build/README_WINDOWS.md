# Windows Packaging Guide

Complete guide for building and packaging Antidetect Browser for Windows.

## Prerequisites

### Required Software

1. **Python 3.12+**
   - Download: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Inno Setup 6.x** (for installer creation)
   - Download: https://jrsoftware.org/isinfo.php
   - Default installation path: `C:\Program Files (x86)\Inno Setup 6`

3. **Windows SDK** (optional, for code signing)
   - Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
   - Required only if you plan to sign the executable

### Python Dependencies

Install all required dependencies:

```bash
pip install -e ".[gui,package]"
```

This installs:
- PyInstaller (for creating executable)
- PyQt6 (GUI framework)
- Pillow & CairoSVG (for icon generation)
- All application dependencies

## Building

### Method 1: Automated Build (Recommended)

#### Using PowerShell (Recommended):

```powershell
.\build\build_windows.ps1
```

Advanced options:
```powershell
# Clean build (removes previous builds)
.\build\build_windows.ps1 -Clean

# Build without installer
.\build\build_windows.ps1 -NoInstaller

# Build with code signing
.\build\build_windows.ps1 -Sign -SignCert "path\to\cert.pfx" -SignPassword "password"
```

#### Using Batch Script:

```batch
build\build_windows.bat
```

This will:
1. Check Python installation
2. Install/update dependencies
3. Generate icons from SVG
4. Clean previous builds
5. Build executable with PyInstaller
6. Create installer with Inno Setup

### Method 2: Manual Build Steps

#### Step 1: Generate Icons

```bash
python build\generate_icons.py
```

This creates:
- `build/icons/icon.ico` - Windows executable icon
- `build/icons/icon_*.png` - Various sizes for Linux

#### Step 2: Build Executable

```bash
python -m PyInstaller antidetect-browser.spec --clean --noconfirm
```

Output: `dist\AntidetectBrowser\AntidetectBrowser.exe`

#### Step 3: Validate Build (Optional)

```bash
python build\validate_build.py
```

This checks:
- Executable exists and is valid
- All required DLLs are present
- Resource files are included
- Icons are available

#### Step 4: Create Installer

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
```

Output: `dist\AntidetectBrowser-Setup-0.1.0.exe`

### Quick Build (Without Installer)

For development/testing:

```batch
build\quick_build.bat
```

This creates just the executable without the installer.

## Output Files

After successful build:

```
dist/
├── AntidetectBrowser/              # Portable application directory
│   ├── AntidetectBrowser.exe       # Main executable
│   ├── python312.dll               # Python runtime
│   ├── PyQt6/                      # Qt libraries
│   ├── antidetect_playwright/      # Application modules
│   └── ...                         # Other dependencies
│
└── AntidetectBrowser-Setup-0.1.0.exe  # Windows installer
```

## Code Signing (Optional)

### Prerequisites

- Code signing certificate (.pfx file)
- Windows SDK installed (for signtool.exe)

### Sign Executable

```powershell
$signTool = "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe"
& (Get-Item $signTool | Sort LastWriteTime -Desc | Select -First 1).FullName `
    sign /f "cert.pfx" /p "password" `
    /tr "http://timestamp.digicert.com" `
    /td SHA256 /fd SHA256 `
    "dist\AntidetectBrowser\AntidetectBrowser.exe"
```

### Automated Signing

Use the PowerShell build script with signing options:

```powershell
.\build\build_windows.ps1 -Sign -SignCert "cert.pfx" -SignPassword "password"
```

This will sign both the executable and the installer.

## Installer Features

The Inno Setup installer includes:

### Installation Options

- **Installation Directory**: Default to `C:\Program Files\Antidetect Browser`
- **User/Admin Mode**: Supports installation without admin rights
- **Desktop Icon**: Optional desktop shortcut
- **Start Menu**: Program group with shortcuts
- **Auto-Update**: Option to enable automatic updates

### Installation Process

1. Welcome screen
2. License agreement
3. Installation directory selection
4. Additional tasks (desktop icon, etc.)
5. Auto-update configuration
6. Installation progress
7. Completion with optional launch

### Uninstallation

The installer creates a proper uninstaller that:
- Removes all application files
- Cleans up Start Menu shortcuts
- Removes desktop icons
- Cleans up application data folders
- Removes registry entries

Access uninstaller via:
- Windows Settings > Apps & features
- Start Menu > Antidetect Browser > Uninstall
- `C:\Program Files\Antidetect Browser\unins000.exe`

## Auto-Update System

### Configuration

Auto-update preference is stored in Windows Registry:
```
HKEY_CURRENT_USER\Software\Antidetect Team\Antidetect Browser\AutoUpdate
```

### How It Works

1. **Update Check**: Application checks GitHub releases API on startup
2. **Notification**: User is notified if update is available
3. **Download**: Update is downloaded to temp directory
4. **Installation**: Installer runs silently and replaces application
5. **Restart**: Application restarts with new version

### Implementation

The auto-update system is implemented in:
- `src/antidetect_playwright/gui/updater.py`

To disable auto-updates, set registry value to 0 or use the GUI settings.

## Troubleshooting

### Build Fails

**Missing Python modules:**
```bash
pip install -e ".[gui,package]" --force-reinstall
```

**PyInstaller errors:**
```bash
# Clean PyInstaller cache
python -m PyInstaller --clean antidetect-browser.spec
```

**Icon generation fails:**
```bash
# Install/reinstall icon dependencies
pip install pillow cairosvg --force-reinstall
```

### Installer Creation Fails

**Inno Setup not found:**
- Check installation path
- Update `INNO_SETUP` variable in build scripts
- Default: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

**Missing files:**
- Run `python build\validate_build.py` to check
- Ensure PyInstaller build completed successfully

### Runtime Errors

**DLL not found:**
- Reinstall dependencies: `pip install -e ".[gui]" --force-reinstall`
- Rebuild with `--clean` flag

**Resource files missing:**
- Check `antidetect-browser.spec` for correct paths
- Ensure all data files are included in `datas` list

**Qt platform plugin missing:**
- Ensure Qt plugins are included in build
- Check `PyQt6/Qt6/plugins/platforms/qwindows.dll` exists

## Advanced Configuration

### Customizing the Build

Edit `antidetect-browser.spec`:

```python
# Exclude unnecessary modules to reduce size
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
]

# Add hidden imports if needed
hiddenimports=[
    'your_module_here',
]

# UPX compression (may reduce size but slower startup)
upx=True,
```

### Customizing the Installer

Edit `build/installer.iss`:

```iss
; Change installation directory
DefaultDirName={autopf}\YourAppName

; Require admin rights
PrivilegesRequired=admin

; Add custom registry entries
[Registry]
Root: HKCU; Subkey: "Software\YourApp"; ValueType: string; ValueName: "Setting"; ValueData: "Value"
```

### Version Management

Update version in multiple locations:

1. `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. `build/version_info.txt`:
   ```python
   filevers=(0, 2, 0, 0),
   prodvers=(0, 2, 0, 0),
   ```

3. `build/installer.iss`:
   ```iss
   #define MyAppVersion "0.2.0"
   ```

4. `src/antidetect_playwright/gui/updater.py`:
   ```python
   CURRENT_VERSION = "0.2.0"
   ```

## File Structure

```
antidetect-playwright/
├── antidetect-browser.spec        # PyInstaller configuration
├── build/
│   ├── icons/                     # Generated icons
│   │   ├── icon.ico               # Windows icon
│   │   └── icon_*.png             # PNG icons (various sizes)
│   ├── installer.iss              # Inno Setup script
│   ├── version_info.txt           # Windows version info
│   ├── windows_manifest.xml       # Windows manifest
│   ├── build_windows.bat          # Batch build script
│   ├── build_windows.ps1          # PowerShell build script
│   ├── quick_build.bat            # Quick build (no installer)
│   ├── generate_icons.py          # Icon generation script
│   ├── validate_build.py          # Build validation script
│   └── README_WINDOWS.md          # This file
├── src/
│   └── antidetect_playwright/
│       └── gui/
│           └── updater.py         # Auto-update implementation
└── dist/                          # Build output (generated)
    ├── AntidetectBrowser/         # Portable application
    └── AntidetectBrowser-Setup-*.exe  # Installer
```

## Deployment

### Manual Distribution

1. Build the installer: `.\build\build_windows.ps1`
2. Test the installer on clean Windows machine
3. Upload `AntidetectBrowser-Setup-0.1.0.exe` to distribution platform

### GitHub Releases

1. Build and sign the installer
2. Create GitHub release with version tag (e.g., `v0.1.0`)
3. Upload signed installer as release asset
4. Auto-update system will detect new release

### Requirements for Auto-Update

- Release tagged with version number (e.g., `v0.1.0`)
- Installer asset name must end with `-Setup.exe`
- Release published as "latest" on GitHub

## Security Considerations

### Code Signing

**Why sign?**
- Prevents "Unknown Publisher" warnings
- Builds user trust
- Prevents tampering

**How to get a certificate:**
1. Purchase from CA (DigiCert, Sectigo, etc.)
2. Follow CA's validation process
3. Receive .pfx certificate file

### Installer Security

- Installer runs with user privileges by default
- No admin rights required
- Files installed to user profile if not admin
- Registry entries in HKCU, not HKLM

### Update Security

- Updates fetched over HTTPS
- GitHub releases provide integrity
- Consider implementing signature verification

## Support & Resources

- **PyInstaller**: https://pyinstaller.org/
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **Code Signing**: https://docs.microsoft.com/en-us/windows/win32/seccrypto/using-signtool-to-sign-a-file
- **Windows SDK**: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

## License

This packaging configuration is part of the Antidetect Browser project and follows the same license.
