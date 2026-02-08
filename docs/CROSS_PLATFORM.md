# Cross-Platform Compatibility Guide

This document describes the cross-platform compatibility features and best practices
implemented in the Antidetect Browser project.

## Supported Platforms

- **Windows**: Windows 7, 8, 10, 11 (64-bit)
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux
- **macOS**: macOS 10.15 (Catalina) and later

## Path Operations

All file path operations use `pathlib.Path` for cross-platform compatibility.

**✓ Good:**
```python
from pathlib import Path

config_dir = Path.home() / ".config" / "app"
config_dir.mkdir(parents=True, exist_ok=True)

data_file = config_dir / "data.json"
data_file.write_text(json.dumps(data), encoding="utf-8")
```

**✗ Bad:**
```python
import os

config_dir = os.path.join(os.path.expanduser("~"), ".config", "app")
os.makedirs(config_dir, exist_ok=True)

data_file = os.path.join(config_dir, "data.json")
with open(data_file, "w") as f:
    json.dump(data, f)
```

## File Permissions

File permissions are handled differently on Windows and Unix systems.

### Unix (Linux/macOS)

Use `chmod` with `stat` module constants:

```python
import stat
from pathlib import Path

file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # Owner read/write only (0o600)
```

### Windows

Windows uses ACLs (Access Control Lists). The `icacls` utility can be used:

```python
import subprocess
import sys

if sys.platform == 'win32':
    subprocess.run([
        'icacls', str(file_path),
        '/inheritance:r',
        '/grant:r', f'{os.environ.get("USERNAME")}:F'
    ], capture_output=True, check=False)
```

### Cross-Platform Permission Handling

See `src/antidetect_playwright/gui/security.py:64-91` for the implemented
cross-platform permission handling in the encryption key file.

## Environment Variables

Use `os.environ` for environment variables, which works across all platforms.

### Platform-Specific Variables

- **Windows**: `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `USERNAME`
- **Unix/Linux/macOS**: `HOME`, `USER`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`

### Cross-Platform Home Directory

Always use `Path.home()` instead of `os.environ.get("HOME")`:

```python
from pathlib import Path

home_dir = Path.home()  # Works on Windows, Linux, macOS
```

## HiDPI/Retina Display Support

### PyQt6 Configuration

HiDPI support is enabled in `src/antidetect_playwright/gui/app.py:1154-1160`:

```python
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Enable HiDPI before creating QApplication
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)
```

### Windows DPI Awareness

Windows DPI awareness is configured via manifest (`build/windows_manifest.xml`):

- **Windows Vista/7/8**: `<dpiAware>true/pm</dpiAware>`
- **Windows 10+**: `<dpiAwareness>permonitorv2,permonitor</dpiAwareness>`

This ensures crisp rendering on high-DPI displays.

### macOS Retina Support

macOS Retina support is enabled in PyInstaller spec (`antidetect-browser.spec:145`):

```python
info_plist={
    'NSHighResolutionCapable': True,
    # ...
}
```

## Line Endings

Python handles line endings automatically when using text mode:

```python
# Automatic line ending conversion
file_path.write_text(content, encoding="utf-8")
content = file_path.read_text(encoding="utf-8")
```

Git is configured via `.gitattributes` to normalize line endings:
- Text files use LF (`\n`) in repository
- Checked out as native line endings on each platform

## Unicode and Special Characters

All file operations use UTF-8 encoding explicitly:

```python
file_path.write_text(content, encoding="utf-8")
content = file_path.read_text(encoding="utf-8")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
```

## Process and Subprocess Management

### Subprocess Calls

Always use `subprocess.run()` with proper error handling:

```python
import subprocess
import sys

try:
    result = subprocess.run(
        ['command', 'arg1', 'arg2'],
        capture_output=True,
        text=True,
        timeout=10,
        check=False  # Don't raise on non-zero exit
    )
except subprocess.TimeoutExpired:
    logger.error("Command timed out")
except FileNotFoundError:
    logger.error("Command not found")
```

### Platform-Specific Commands

Use `sys.platform` to detect platform and choose appropriate commands:

```python
import sys

if sys.platform == 'win32':
    # Windows-specific code
    cmd = ['icacls', ...]
elif sys.platform == 'darwin':
    # macOS-specific code
    cmd = ['chmod', ...]
else:
    # Linux/Unix code
    cmd = ['chmod', ...]
```

## PyInstaller Packaging

### Platform-Specific Configurations

The PyInstaller spec file handles platform differences:

- **Icons**:
  - Windows: `icon.ico`
  - macOS: `icon.icns`
  - Linux: No icon in executable (use desktop file)

- **Manifests**:
  - Windows: `build/windows_manifest.xml` (DPI awareness, compatibility)
  - macOS: `info_plist` in BUNDLE
  - Linux: No manifest

- **Version Info**:
  - Windows: `build/version_info.txt`
  - Other platforms: None

### Testing Builds

Test on each target platform before release:

```bash
# Windows
pyinstaller antidetect-browser.spec
dist/AntidetectBrowser/AntidetectBrowser.exe

# Linux
pyinstaller antidetect-browser.spec
dist/AntidetectBrowser/AntidetectBrowser

# macOS
pyinstaller antidetect-browser.spec
open dist/AntidetectBrowser.app
```

## Platform-Specific Fallbacks

### Browser Paths

Browser executable paths differ by platform:

```python
from pathlib import Path
import sys

if sys.platform == 'win32':
    browser_path = Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'Firefox'
elif sys.platform == 'darwin':
    browser_path = Path('/Applications/Firefox.app/Contents/MacOS/firefox')
else:
    browser_path = Path('/usr/bin/firefox')
```

Camoufox handles this automatically via `playwright`.

### Data Directories

Standard data directory locations:

- **Windows**: `%APPDATA%/AntidetectBrowser`
- **Linux**: `~/.local/share/antidetect-browser` or `$XDG_DATA_HOME/antidetect-browser`
- **macOS**: `~/Library/Application Support/AntidetectBrowser`

We use a simple `data/` directory in the current working directory for portability.

## Testing Cross-Platform Compatibility

Run the compatibility test suite:

```bash
python tests/test_cross_platform.py
```

This tests:
- Path operations
- File permissions
- Environment variables
- Platform detection
- Line endings
- Unicode paths

## Common Pitfalls

### ❌ Hardcoded Path Separators

```python
# BAD: Hardcoded separators
config_path = "data/config.json"  # Fails on Windows if using backslashes

# GOOD: Use Path
config_path = Path("data") / "config.json"
```

### ❌ Platform-Specific System Calls

```python
# BAD: Unix-only chmod
os.chmod(file_path, 0o600)

# GOOD: Platform-aware permission handling
if sys.platform != 'win32':
    file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
else:
    # Windows ACL handling
    pass
```

### ❌ Assuming Case-Sensitive Filesystem

```python
# BAD: May fail on case-insensitive filesystems (Windows, macOS default)
if Path("MyFile.txt").exists():
    pass

# GOOD: Use exact case
if Path("myfile.txt").exists():  # Consistent naming
    pass
```

## Best Practices Summary

1. **Always use `pathlib.Path`** for file operations
2. **Handle permissions platform-aware** (chmod on Unix, ACL on Windows)
3. **Use `Path.home()`** instead of environment variables for home directory
4. **Explicit UTF-8 encoding** for all text file operations
5. **Enable HiDPI support** for PyQt6 applications
6. **Test on all target platforms** before release
7. **Use platform detection** (`sys.platform`) for platform-specific code
8. **Avoid hardcoded paths** and path separators
9. **Handle subprocess errors** gracefully
10. **Document platform-specific behavior** in code comments

## Resources

- [pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [PyQt6 HiDPI support](https://doc.qt.io/qt-6/highdpi.html)
- [PyInstaller cross-platform](https://pyinstaller.org/en/stable/requirements.html)
- [Windows DPI awareness](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows)
