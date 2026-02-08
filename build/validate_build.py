#!/usr/bin/env python3
"""
Validate Windows build before creating installer.
Checks for:
- Required DLLs
- Resource files
- Icon files
- Dependencies
"""

import sys
from pathlib import Path


def check_build_directory() -> bool:
    """Check if build directory exists and contains required files."""
    build_dir = Path("dist/AntidetectBrowser")

    if not build_dir.exists():
        print("✗ Build directory not found: dist/AntidetectBrowser")
        return False

    print("✓ Build directory found")

    # Check executable
    exe_path = build_dir / "AntidetectBrowser.exe"
    if not exe_path.exists():
        print("✗ Main executable not found")
        return False

    print(f"✓ Executable found ({exe_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Check for critical DLLs
    critical_dlls = [
        "python312.dll",
        "PyQt6/Qt6/bin/Qt6Core.dll",
        "PyQt6/Qt6/bin/Qt6Gui.dll",
        "PyQt6/Qt6/bin/Qt6Widgets.dll",
    ]

    missing_dlls = []
    for dll in critical_dlls:
        dll_path = build_dir / dll
        if not dll_path.exists():
            missing_dlls.append(dll)

    if missing_dlls:
        print("✗ Missing critical DLLs:")
        for dll in missing_dlls:
            print(f"  - {dll}")
        return False

    print(f"✓ All critical DLLs present")

    # Check resource files
    resource_dirs = [
        "antidetect_playwright/resources/chrome",
        "browserforge/fingerprints/data",
    ]

    for resource_dir in resource_dirs:
        resource_path = build_dir / resource_dir
        if not resource_path.exists():
            print(f"✗ Missing resource directory: {resource_dir}")
            return False

    print("✓ Resource files present")

    # Calculate total size
    total_size = sum(f.stat().st_size for f in build_dir.rglob("*") if f.is_file())
    print(f"\nTotal build size: {total_size / 1024 / 1024:.1f} MB")

    return True


def check_icon_files() -> bool:
    """Check if icon files are present."""
    icons_dir = Path("build/icons")

    if not icons_dir.exists():
        print("✗ Icons directory not found")
        return False

    ico_path = icons_dir / "icon.ico"
    if not ico_path.exists():
        print("✗ Windows icon (icon.ico) not found")
        return False

    print("✓ Icon files present")
    return True


def check_installer_script() -> bool:
    """Check if Inno Setup script exists."""
    iss_path = Path("build/installer.iss")

    if not iss_path.exists():
        print("✗ Installer script not found")
        return False

    print("✓ Installer script present")
    return True


def main() -> int:
    """Main validation function."""
    print("=" * 50)
    print("Antidetect Browser - Build Validation")
    print("=" * 50)
    print()

    checks = [
        ("Build Directory", check_build_directory),
        ("Icon Files", check_icon_files),
        ("Installer Script", check_installer_script),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All validation checks passed!")
        print("Ready to create installer.")
        return 0
    else:
        print("✗ Some validation checks failed.")
        print("Please fix issues before creating installer.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
