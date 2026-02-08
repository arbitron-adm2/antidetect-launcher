# Windows Packaging - Quick Start Guide

## Quick Build Commands

### Full Build with Installer (PowerShell - Recommended)
```powershell
.\build\build_windows.ps1
```

### Full Build with Installer (Batch)
```batch
build\build_windows.bat
```

### Quick Build (Executable Only)
```batch
build\quick_build.bat
```

### With Code Signing
```powershell
.\build\build_windows.ps1 -Sign -SignCert "cert.pfx" -SignPassword "your_password"
```

## What You Get

### After Build:
- `dist\AntidetectBrowser\AntidetectBrowser.exe` - Portable executable
- `dist\AntidetectBrowser-Setup-0.1.0.exe` - Windows installer

### Installer Features:
- ✅ Proper Start Menu shortcuts
- ✅ Optional desktop icon
- ✅ Auto-update configuration
- ✅ Uninstaller
- ✅ No admin rights required
- ✅ Windows 10/11 compatible
- ✅ High DPI support
- ✅ Version info & icon

## Prerequisites

1. **Python 3.12+**: https://www.python.org/downloads/
2. **Inno Setup 6**: https://jrsoftware.org/isinfo.php (for installer)
3. Install dependencies: `pip install -e ".[gui,package]"`

## Files Created

```
build/
├── README_WINDOWS.md           # Detailed documentation
├── installer.iss               # Inno Setup script
├── version_info.txt            # Windows version info
├── windows_manifest.xml        # Windows manifest
├── build_windows.bat           # Batch build script
├── build_windows.ps1           # PowerShell build script (recommended)
├── quick_build.bat             # Quick build (no installer)
├── generate_icons.py           # Icon generation
└── validate_build.py           # Build validation

src/antidetect_playwright/gui/
└── updater.py                  # Auto-update system

antidetect-browser.spec         # Updated with Windows version info
```

## Next Steps

1. **Test Build**: Run `.\build\build_windows.ps1`
2. **Test Installer**: Install on clean Windows VM
3. **Test Auto-Update**: Verify update checking works
4. **Code Signing**: Obtain certificate and sign executables
5. **Deploy**: Upload to GitHub releases or distribution platform

## Documentation

See `build/README_WINDOWS.md` for:
- Detailed build instructions
- Troubleshooting guide
- Code signing setup
- Auto-update configuration
- Deployment strategies
- Advanced customization

## Support

For issues or questions:
- Check `build/README_WINDOWS.md`
- Run validation: `python build\validate_build.py`
- Check build logs
