# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Antidetect Launcher GUI."""

import sys
from pathlib import Path
import site

block_cipher = None

# Project paths
project_root = Path(SPECPATH)
src_dir = project_root / "src"
resources_dir = src_dir / "antidetect_launcher/resources"
icon_path = project_root / "build/icons"

# Find browserforge data directory
site_packages = Path(site.getsitepackages()[0])
browserforge_data = site_packages / "browserforge"
camoufox_pkg = site_packages / "camoufox"
language_tags_pkg = site_packages / "language_tags"

# Platform-specific icon and version info
if sys.platform == "win32":
    _ico = icon_path / "icon.ico"
    icon_file = str(_ico) if _ico.exists() else None
elif sys.platform == "darwin":
    _icns = icon_path / "icon.icns"
    icon_file = str(_icns) if _icns.exists() else None
else:
    icon_file = None

# Collect all resource files
datas = []

# App resources (always present)
for res in ("chrome", "icon.svg", "app-icon-256.svg", "tray-icon.svg", "default_config"):
    p = resources_dir / res
    if p.exists():
        dest = "antidetect_launcher/resources/" + ("chrome" if res == "chrome" else (
            "default_config" if res == "default_config" else ""))
        if p.is_dir():
            datas.append((str(p), f"antidetect_launcher/resources/{res}"))
        else:
            datas.append((str(p), "antidetect_launcher/resources"))

# External package data (optional — included when present)
_optional_data = [
    (browserforge_data / "fingerprints/data", "browserforge/fingerprints/data"),
    (browserforge_data / "headers/data",      "browserforge/headers/data"),
    (camoufox_pkg,                             "camoufox"),
    (language_tags_pkg / "data",               "language_tags/data"),
]
for src, dest in _optional_data:
    if src.exists():
        datas.append((str(src), dest))

# Add config files (from .config/ if present, else from resources/default_config)
config_dir = project_root / ".config"
default_config_dir = resources_dir / "default_config"
for cfg_name in ("app.toml", "runtime.toml", "logging.toml"):
    cfg = config_dir / cfg_name
    if not cfg.exists():
        cfg = default_config_dir / cfg_name
    if cfg.exists():
        datas.append((str(cfg), "config"))

# Hidden imports (packages not auto-detected)
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'qasync',
    'camoufox',
    'camoufox.async_api',
    'camoufox.ip',
    'camoufox.locale',
    'camoufox.fingerprints',
    'camoufox.webgl',
    'browserforge',
    'browserforge.fingerprints',
    'playwright',
    'playwright.async_api',
    'aiohttp',
    'aiohttp_socks',
    'cryptography',
    'orjson',
]

a = Analysis(
    [str(src_dir / "antidetect_launcher/gui/launcher_pyinstaller.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'PIL.ImageQt',  # Exclude unused PIL modules
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AntidetectLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='build/version_info.txt' if sys.platform == "win32" and (project_root / 'build/version_info.txt').exists() else None,
    manifest='build/windows_manifest.xml' if sys.platform == "win32" and (project_root / 'build/windows_manifest.xml').exists() else None,
    uac_admin=False,  # Don't require admin rights
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AntidetectLauncher',
)

# macOS app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name='AntidetectLauncher.app',
        icon=icon_file,
        bundle_identifier='com.antidetect.browser',
        info_plist={
            'CFBundleName': 'Antidetect Launcher',
            'CFBundleDisplayName': 'Antidetect Launcher',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15.0',
        },
    )
