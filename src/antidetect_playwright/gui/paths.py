"""Platform-specific paths for application data."""

import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """Get platform-specific data directory for the application.

    Returns:
        Path to data directory based on platform and installation method:

        Development mode (running from source):
            - ./data/ (relative to project root)

        Installed package:
            Linux:   ~/.local/share/antidetect-browser/
            Windows: %APPDATA%/AntidetectBrowser/
            macOS:   ~/Library/Application Support/AntidetectBrowser/

    The function detects if running from installed package by checking
    if the executable is frozen (PyInstaller) or installed via package manager.
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return _get_user_data_dir()

    # Check if installed via package manager (Linux)
    if sys.platform.startswith('linux'):
        # If running from /usr/bin or /usr/local/bin, assume installed package
        exe_path = Path(sys.argv[0]).resolve()
        if str(exe_path).startswith(('/usr/bin', '/usr/local/bin', '/opt')):
            return _get_user_data_dir()

    # Development mode - use local data directory
    # Find project root (where this file is located, go up to src parent)
    current_file = Path(__file__).resolve()
    # From: src/antidetect_playwright/gui/paths.py
    # To:   project_root/
    project_root = current_file.parent.parent.parent.parent
    return project_root / "data"


def _get_user_data_dir() -> Path:
    """Get user-specific data directory based on platform."""
    if sys.platform == 'win32':
        # Windows: %APPDATA%/AntidetectBrowser/
        appdata = os.environ.get('APPDATA')
        if appdata:
            data_dir = Path(appdata) / "AntidetectBrowser"
        else:
            # Fallback to user home
            data_dir = Path.home() / ".antidetect_browser"

    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/AntidetectBrowser/
        data_dir = Path.home() / "Library" / "Application Support" / "AntidetectBrowser"

    else:
        # Linux: follow XDG Base Directory specification
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            data_dir = Path(xdg_data_home) / "antidetect-browser"
        else:
            # Default: ~/.local/share/antidetect-browser/
            data_dir = Path.home() / ".local" / "share" / "antidetect-browser"

    # Create directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


def get_config_dir() -> Path:
    """Get platform-specific config directory.

    Returns:
        Path to config directory:

        Linux:   ~/.config/antidetect-browser/
        Windows: Same as data dir
        macOS:   Same as data dir
    """
    if sys.platform.startswith('linux') and not getattr(sys, 'frozen', False):
        # Development mode - use project config
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        return project_root / "config"

    if sys.platform.startswith('linux'):
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / "antidetect-browser"
        else:
            config_dir = Path.home() / ".config" / "antidetect-browser"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    # For Windows and macOS, config is in data dir
    return get_data_dir()


def get_cache_dir() -> Path:
    """Get platform-specific cache directory.

    Returns:
        Path to cache directory:

        Linux:   ~/.cache/antidetect-browser/
        Windows: %LOCALAPPDATA%/AntidetectBrowser/Cache/
        macOS:   ~/Library/Caches/AntidetectBrowser/
    """
    if getattr(sys, 'frozen', False) or sys.platform != 'linux':
        if sys.platform == 'win32':
            localappdata = os.environ.get('LOCALAPPDATA')
            if localappdata:
                cache_dir = Path(localappdata) / "AntidetectBrowser" / "Cache"
            else:
                cache_dir = Path.home() / ".antidetect_browser" / "cache"

        elif sys.platform == 'darwin':
            cache_dir = Path.home() / "Library" / "Caches" / "AntidetectBrowser"

        else:
            # Linux
            xdg_cache_home = os.environ.get('XDG_CACHE_HOME')
            if xdg_cache_home:
                cache_dir = Path(xdg_cache_home) / "antidetect-browser"
            else:
                cache_dir = Path.home() / ".cache" / "antidetect-browser"

        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    # Development mode
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    cache_dir = project_root / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_logs_dir() -> Path:
    """Get platform-specific logs directory.

    Returns:
        Path to logs directory (subdirectory of data dir)
    """
    logs_dir = get_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def is_development_mode() -> bool:
    """Check if running in development mode (from source)."""
    return not getattr(sys, 'frozen', False)


def is_installed_package() -> bool:
    """Check if running as installed package."""
    if getattr(sys, 'frozen', False):
        return True

    if sys.platform.startswith('linux'):
        exe_path = Path(sys.argv[0]).resolve()
        return str(exe_path).startswith(('/usr/bin', '/usr/local/bin', '/opt'))

    return False
