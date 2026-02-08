#!/usr/bin/env python3
"""Check system requirements and dependencies."""

import sys
import platform
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.12+."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("  ✗ FAILED: Python 3.12+ required")
        return False
    
    print("  ✓ OK")
    return True


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if package is installed and importable."""
    import_name = import_name or package_name
    
    try:
        __import__(import_name)
        import importlib.metadata as metadata
        version = metadata.version(package_name)
        print(f"  ✓ {package_name} {version}")
        return True
    except ImportError:
        print(f"  ✗ {package_name} NOT INSTALLED")
        return False
    except Exception as e:
        print(f"  ⚠ {package_name} ERROR: {e}")
        return False


def check_system_libs():
    """Check system libraries (Linux only)."""
    if platform.system() != "Linux":
        return True
    
    print("\nSystem libraries (Linux):")
    
    libs_to_check = [
        "libnss3.so",
        "libatk-1.0.so.0",
        "libcups.so.2",
        "libxkbcommon.so.0",
    ]
    
    all_ok = True
    for lib in libs_to_check:
        result = subprocess.run(
            ["ldconfig", "-p"],
            capture_output=True,
            text=True
        )
        if lib in result.stdout:
            print(f"  ✓ {lib}")
        else:
            print(f"  ✗ {lib} NOT FOUND")
            all_ok = False
    
    if not all_ok:
        print("\n  Install missing libraries:")
        print("    Ubuntu/Debian: sudo apt install libnss3 libatk1.0-0 libcups2 libxkbcommon0")
        print("    Fedora/RHEL: sudo dnf install nss atk cups-libs libxkbcommon")
    
    return all_ok


def check_display():
    """Check if display is available (for GUI)."""
    if platform.system() == "Linux":
        import os
        display = os.environ.get("DISPLAY")
        if display:
            print(f"  ✓ DISPLAY={display}")
            return True
        else:
            print("  ✗ DISPLAY not set (GUI won't work)")
            print("    Run on a system with X11 or Wayland display server")
            return False
    return True


def main():
    """Run all checks."""
    print("=== System Requirements Check ===\n")
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print()
    
    checks = []
    
    # Python version
    checks.append(check_python_version())
    
    # Required packages
    print("\nCore dependencies:")
    checks.append(check_package("camoufox"))
    checks.append(check_package("playwright"))
    checks.append(check_package("aiohttp"))
    checks.append(check_package("redis"))
    checks.append(check_package("cryptography"))
    checks.append(check_package("click"))
    checks.append(check_package("orjson"))
    
    print("\nGUI dependencies:")
    checks.append(check_package("PyQt6"))
    checks.append(check_package("qasync"))
    
    # System libs
    if platform.system() == "Linux":
        checks.append(check_system_libs())
        checks.append(check_display())
    
    # Check data directory
    print("\nData directory:")
    data_dir = Path("data")
    if data_dir.exists():
        print(f"  ✓ {data_dir.absolute()}")
    else:
        print(f"  ⚠ {data_dir.absolute()} does not exist (will be created)")
    
    # Summary
    print("\n" + "=" * 50)
    if all(checks):
        print("✓ All checks passed! System is ready.")
        return 0
    else:
        print("✗ Some checks failed. Fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
