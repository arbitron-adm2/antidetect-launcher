"""Cross-platform autostart management for Antidetect Browser."""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = "Antidetect Browser"
APP_ID = "antidetect-browser"

# Linux autostart desktop entry template
_LINUX_AUTOSTART_TEMPLATE = """[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Anti-detection browser automation
Exec={exec_path}
Icon={icon}
Terminal=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
"""


def is_autostart_enabled() -> bool:
    """Check if autostart is enabled on the current platform."""
    if sys.platform == "win32":
        return _win_is_autostart()
    elif sys.platform == "darwin":
        return _mac_is_autostart()
    else:
        return _linux_is_autostart()


def set_autostart(enabled: bool) -> bool:
    """Enable or disable autostart.

    Returns True if the operation succeeded.
    """
    try:
        if sys.platform == "win32":
            return _win_set_autostart(enabled)
        elif sys.platform == "darwin":
            return _mac_set_autostart(enabled)
        else:
            return _linux_set_autostart(enabled)
    except Exception as e:
        logger.exception("Failed to set autostart to %s: %s", enabled, e)
        return False


# --- Linux ---


def _linux_autostart_path() -> Path:
    """Get path to autostart .desktop file."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "autostart" / f"{APP_ID}.desktop"
    return Path.home() / ".config" / "autostart" / f"{APP_ID}.desktop"


def _linux_find_exec() -> str:
    """Find the executable path for the .desktop Exec= field."""
    # Check common install locations
    for candidate in [
        "/usr/bin/antidetect-browser",
        "/usr/local/bin/antidetect-browser",
        "/opt/antidetect-browser/AntidetectBrowser",
    ]:
        if Path(candidate).exists():
            return candidate

    # Fallback to current executable
    return sys.argv[0]


def _linux_is_autostart() -> bool:
    """Check if Linux autostart .desktop file exists and is enabled."""
    path = _linux_autostart_path()
    if not path.exists():
        return False
    content = path.read_text()
    # X-GNOME-Autostart-enabled=false means disabled
    if "X-GNOME-Autostart-enabled=false" in content:
        return False
    return True


def _linux_set_autostart(enabled: bool) -> bool:
    """Create or remove Linux autostart .desktop file."""
    path = _linux_autostart_path()

    if not enabled:
        if path.exists():
            path.unlink()
            logger.info("Removed autostart: %s", path)
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    content = _LINUX_AUTOSTART_TEMPLATE.format(
        name=APP_NAME,
        exec_path=_linux_find_exec(),
        icon=APP_ID,
    )
    path.write_text(content)
    logger.info("Created autostart: %s", path)
    return True


# --- Windows ---


def _win_is_autostart() -> bool:
    """Check Windows registry for autostart entry."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def _win_set_autostart(enabled: bool) -> bool:
    """Set or remove Windows registry autostart entry."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            if enabled:
                exe_path = sys.executable
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
                logger.info("Windows autostart enabled")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    logger.info("Windows autostart disabled")
                except FileNotFoundError:
                    pass
            return True
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        logger.exception("Failed to set Windows autostart: %s", e)
        return False


# --- macOS ---

_MAC_PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.antidetect.browser.plist"

_MAC_PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.antidetect.browser</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exec_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""


def _mac_is_autostart() -> bool:
    """Check if macOS LaunchAgent plist exists."""
    return _MAC_PLIST_PATH.exists()


def _mac_set_autostart(enabled: bool) -> bool:
    """Create or remove macOS LaunchAgent plist."""
    if not enabled:
        if _MAC_PLIST_PATH.exists():
            _MAC_PLIST_PATH.unlink()
            logger.info("Removed macOS autostart")
        return True

    _MAC_PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    exec_path = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
    _MAC_PLIST_PATH.write_text(_MAC_PLIST_TEMPLATE.format(exec_path=exec_path))
    logger.info("Created macOS autostart: %s", _MAC_PLIST_PATH)
    return True
