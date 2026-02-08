#!/usr/bin/env python3
"""
Validate all build configurations are consistent.

Checks:
- Version numbers match across files
- Required files exist
- Icon files are present
- Build scripts are executable
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_section(title: str) -> None:
    """Print section header."""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_check(name: str, passed: bool, details: str = "") -> None:
    """Print check result."""
    symbol = "✓" if passed else "✗"
    color = Colors.GREEN if passed else Colors.RED
    status = "PASS" if passed else "FAIL"

    print(f"{color}{symbol} {name:<40} [{status}]{Colors.END}")
    if details:
        print(f"  {details}")


def get_version_from_file(file_path: Path, pattern: str) -> str:
    """Extract version from file using regex pattern."""
    if not file_path.exists():
        return None

    content = file_path.read_text()
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1) if match else None


def check_version_consistency() -> Tuple[bool, List[str]]:
    """Check version consistency across files."""
    project_root = Path(__file__).parent.parent.parent

    versions = {
        "pyproject.toml": get_version_from_file(
            project_root / "pyproject.toml",
            r'^version = "([^"]+)"'
        ),
        "version_info.txt": get_version_from_file(
            project_root / "build/version_info.txt",
            r"'FileVersion', u'([^']+)'"
        ),
        "installer.iss": get_version_from_file(
            project_root / "build/installer.iss",
            r'#define MyAppVersion "([^"]+)"'
        ),
        "updater.py": get_version_from_file(
            project_root / "src/antidetect_playwright/gui/updater.py",
            r'CURRENT_VERSION = "([^"]+)"'
        ),
    }

    # Remove None values and version suffixes
    versions = {
        k: v.split('.0')[0] if v and '.0' in v else v
        for k, v in versions.items()
        if v is not None
    }

    if not versions:
        return False, ["No version files found"]

    unique_versions = set(versions.values())

    if len(unique_versions) == 1:
        return True, [f"All versions match: {unique_versions.pop()}"]
    else:
        details = [f"{k}: {v}" for k, v in versions.items()]
        return False, ["Version mismatch:"] + details


def check_required_files() -> Tuple[bool, List[str]]:
    """Check required files exist."""
    project_root = Path(__file__).parent.parent.parent

    required_files = [
        "pyproject.toml",
        "antidetect-browser.spec",
        "build/version_info.txt",
        "build/windows_manifest.xml",
        "build/installer.iss",
        "build/build_windows.ps1",
        "build/build_windows.bat",
        "build/generate_icons.py",
        "src/antidetect_playwright/gui/updater.py",
    ]

    missing = []
    for file in required_files:
        if not (project_root / file).exists():
            missing.append(file)

    if not missing:
        return True, [f"All {len(required_files)} required files exist"]
    else:
        return False, ["Missing files:"] + missing


def check_icon_files() -> Tuple[bool, List[str]]:
    """Check icon files exist."""
    project_root = Path(__file__).parent.parent.parent
    icons_dir = project_root / "build/icons"

    if not icons_dir.exists():
        return False, ["Icons directory not found: build/icons"]

    required_icons = {
        "Windows": "icon.ico",
        "Linux": "icon_128x128.png",
    }

    missing = []
    for platform, icon in required_icons.items():
        if not (icons_dir / icon).exists():
            missing.append(f"{platform}: {icon}")

    if not missing:
        return True, ["All platform icons exist"]
    else:
        return False, ["Missing icons:"] + missing


def check_executable_scripts() -> Tuple[bool, List[str]]:
    """Check build scripts are executable (Linux/macOS)."""
    if sys.platform == "win32":
        return True, ["Skipped (Windows platform)"]

    project_root = Path(__file__).parent.parent.parent

    scripts = [
        "build/scripts/build_deb.sh",
        "build/scripts/build_appimage.sh",
        "build/scripts/build_flatpak.sh",
    ]

    non_executable = []
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            if not script_path.stat().st_mode & 0o111:
                non_executable.append(script)

    if not non_executable:
        return True, ["All scripts are executable"]
    else:
        return False, ["Non-executable scripts:"] + non_executable


def check_workflows() -> Tuple[bool, List[str]]:
    """Check GitHub Actions workflows exist."""
    project_root = Path(__file__).parent.parent.parent
    workflows_dir = project_root / ".github/workflows"

    if not workflows_dir.exists():
        return False, [".github/workflows directory not found"]

    required_workflows = [
        "build-windows.yml",
        "build-linux.yml",
        "ci.yml",
    ]

    missing = []
    for workflow in required_workflows:
        if not (workflows_dir / workflow).exists():
            missing.append(workflow)

    if not missing:
        return True, ["All workflows exist"]
    else:
        return False, ["Missing workflows:"] + missing


def main() -> None:
    """Main validation function."""
    print_section("Build Configuration Validation")

    checks = [
        ("Version Consistency", check_version_consistency),
        ("Required Files", check_required_files),
        ("Icon Files", check_icon_files),
        ("Executable Scripts", check_executable_scripts),
        ("GitHub Workflows", check_workflows),
    ]

    all_passed = True

    for check_name, check_func in checks:
        passed, details = check_func()
        print_check(check_name, passed, "\n  ".join(details))

        if not passed:
            all_passed = False

    print_section("Summary")

    if all_passed:
        print(f"{Colors.GREEN}✅ All validation checks passed!{Colors.END}")
        print("\nReady to build:")
        print("  Windows: .\\build\\build_windows.ps1")
        print("  Linux:   ./build/scripts/build_deb.sh")
        return 0
    else:
        print(f"{Colors.RED}❌ Some validation checks failed{Colors.END}")
        print("\nPlease fix the issues above before building.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
