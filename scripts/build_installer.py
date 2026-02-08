#!/usr/bin/env python3
"""Build Windows installer using NSIS."""

import subprocess
import sys
from pathlib import Path


def get_version():
    """Get version from pyproject.toml."""
    import tomllib
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def create_nsis_script(version):
    """Create NSIS installer script."""
    project_root = Path(__file__).parent.parent

    nsis_script = f"""
; Antidetect Browser Installer Script
; Generated automatically

!include "MUI2.nsh"

; Installer details
Name "Antidetect Browser"
OutFile "dist\\AntidetectBrowser-Setup-{version}.exe"
InstallDir "$PROGRAMFILES64\\AntidetectBrowser"
InstallDirRegKey HKLM "Software\\AntidetectBrowser" "InstallDir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "build\\icons\\icon.ico"
!define MUI_UNICON "build\\icons\\icon.ico"

; Pages
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "{version}.0"
VIAddVersionKey "ProductName" "Antidetect Browser"
VIAddVersionKey "FileDescription" "Antidetect Browser Installer"
VIAddVersionKey "FileVersion" "{version}"
VIAddVersionKey "ProductVersion" "{version}"
VIAddVersionKey "LegalCopyright" "© 2024 Antidetect Team"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"

    ; Copy all files
    File /r "dist\\AntidetectBrowser\\*.*"

    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Antidetect Browser"
    CreateShortcut "$SMPROGRAMS\\Antidetect Browser\\Antidetect Browser.lnk" "$INSTDIR\\AntidetectBrowser.exe"
    CreateShortcut "$DESKTOP\\Antidetect Browser.lnk" "$INSTDIR\\AntidetectBrowser.exe"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"

    ; Registry keys
    WriteRegStr HKLM "Software\\AntidetectBrowser" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser" "DisplayName" "Antidetect Browser"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser" "DisplayIcon" "$INSTDIR\\AntidetectBrowser.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser" "Publisher" "Antidetect Team"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser" "DisplayVersion" "{version}"

SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\\Antidetect Browser.lnk"
    RMDir /r "$SMPROGRAMS\\Antidetect Browser"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\\AntidetectBrowser"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntidetectBrowser"

SectionEnd
"""

    nsis_file = project_root / "installer.nsi"
    with open(nsis_file, "w") as f:
        f.write(nsis_script)

    return nsis_file


def build_installer():
    """Build installer with NSIS."""
    version = get_version()
    print(f"Building Windows installer v{version}...")

    # Create NSIS script
    nsis_script = create_nsis_script(version)
    print(f"NSIS script created: {nsis_script}")

    # Check if NSIS is installed
    try:
        # Try common NSIS paths
        nsis_paths = [
            r"C:\Program Files (x86)\NSIS\makensis.exe",
            r"C:\Program Files\NSIS\makensis.exe",
            "makensis.exe"  # In PATH
        ]

        nsis_exe = None
        for path in nsis_paths:
            if Path(path).exists() or path == "makensis.exe":
                nsis_exe = path
                break

        if not nsis_exe:
            print("ERROR: NSIS not found!")
            print("Please install NSIS from https://nsis.sourceforge.io/")
            print("Or run: choco install nsis")
            return False

        # Build installer
        print(f"Running NSIS compiler...")
        subprocess.run([nsis_exe, str(nsis_script)], check=True)

        print("\n=== Installer created successfully! ===")
        print(f"Installer: dist/AntidetectBrowser-Setup-{version}.exe")
        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: NSIS compilation failed: {e}")
        return False
    except FileNotFoundError:
        print("ERROR: NSIS not found in PATH")
        print("Install NSIS: choco install nsis")
        return False


if __name__ == "__main__":
    success = build_installer()
    sys.exit(0 if success else 1)
