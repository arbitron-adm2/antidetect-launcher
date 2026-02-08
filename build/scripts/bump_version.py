#!/usr/bin/env python3
"""
Bump version across all configuration files (Windows + Linux).

Usage:
    python bump_version.py 0.2.0
    python bump_version.py --major
    python bump_version.py --minor
    python bump_version.py --patch

Supports:
    - Windows: pyproject.toml, version_info.txt, installer.iss, updater.py
    - Linux: debian/changelog, AppImage manifests, Flatpak manifests
"""

import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string to tuple."""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, match.groups()))


def increment_version(version: str, part: str) -> str:
    """Increment version by part (major, minor, patch)."""
    major, minor, patch = parse_version(version)

    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid part: {part}")


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject.read_text()

    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)

    raise ValueError("Version not found in pyproject.toml")


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml."""
    file_path = Path(__file__).parent.parent / "pyproject.toml"
    content = file_path.read_text()

    content = re.sub(
        r'^version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )

    file_path.write_text(content)
    print(f"✓ Updated pyproject.toml")


def update_version_info(new_version: str) -> None:
    """Update Windows version info."""
    file_path = Path(__file__).parent / "version_info.txt"
    if not file_path.exists():
        print(f"⚠ Skipped version_info.txt (not found)")
        return

    content = file_path.read_text()
    major, minor, patch = parse_version(new_version)
    version_tuple = f"({major}, {minor}, {patch}, 0)"

    content = re.sub(
        r'filevers=\([^)]+\)',
        f'filevers={version_tuple}',
        content
    )
    content = re.sub(
        r'prodvers=\([^)]+\)',
        f'prodvers={version_tuple}',
        content
    )
    content = re.sub(
        r"'FileVersion', u'[^']+",
        f"'FileVersion', u'{new_version}.0",
        content
    )
    content = re.sub(
        r"'ProductVersion', u'[^']+",
        f"'ProductVersion', u'{new_version}.0",
        content
    )

    file_path.write_text(content)
    print(f"✓ Updated version_info.txt")


def update_inno_setup(new_version: str) -> None:
    """Update Inno Setup script."""
    file_path = Path(__file__).parent / "installer.iss"
    if not file_path.exists():
        print(f"⚠ Skipped installer.iss (not found)")
        return

    content = file_path.read_text()

    content = re.sub(
        r'#define MyAppVersion "[^"]+"',
        f'#define MyAppVersion "{new_version}"',
        content
    )

    file_path.write_text(content)
    print(f"✓ Updated installer.iss")


def update_updater_py(new_version: str) -> None:
    """Update auto-updater version."""
    file_path = Path(__file__).parent.parent / "src/antidetect_playwright/gui/updater.py"
    if not file_path.exists():
        print(f"⚠ Skipped updater.py (not found)")
        return

    content = file_path.read_text()

    content = re.sub(
        r'CURRENT_VERSION = "[^"]+"',
        f'CURRENT_VERSION = "{new_version}"',
        content
    )

    file_path.write_text(content)
    print(f"✓ Updated updater.py")


def update_github_workflows(new_version: str) -> None:
    """Update version in GitHub workflows."""
    workflows_dir = Path(__file__).parent.parent.parent / ".github/workflows"
    if not workflows_dir.exists():
        print(f"⚠ Skipped GitHub workflows (directory not found)")
        return

    for workflow_file in workflows_dir.glob("*.yml"):
        content = workflow_file.read_text()
        original = content

        content = re.sub(
            r"APP_VERSION: '[^']+'",
            f"APP_VERSION: '{new_version}'",
            content
        )

        if content != original:
            workflow_file.write_text(content)
            print(f"✓ Updated {workflow_file.name}")


def update_debian_changelog(new_version: str) -> None:
    """Update debian/changelog file."""
    project_root = Path(__file__).parent.parent.parent
    changelog_file = project_root / "debian/changelog"

    if not changelog_file.exists():
        print(f"⚠ Skipped debian/changelog (not found)")
        return

    # Check if dch (debchange) is available
    try:
        # Try using dch for proper changelog entry
        result = subprocess.run(
            ["dch", "--version"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            # Use dch for proper formatting
            subprocess.run(
                [
                    "dch",
                    "-v", f"{new_version}-1",
                    "-D", "unstable",
                    f"Release version {new_version}"
                ],
                cwd=project_root,
                check=True
            )
            print(f"✓ Updated debian/changelog (via dch)")
            return
    except FileNotFoundError:
        pass

    # Fallback: manual update
    timestamp = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

    new_entry = f"""antidetect-browser ({new_version}-1) unstable; urgency=medium

  * Release version {new_version}

 -- Antidetect Team <support@antidetect.io>  {timestamp}

"""

    # Read existing changelog
    existing_content = changelog_file.read_text() if changelog_file.exists() else ""

    # Prepend new entry
    new_content = new_entry + existing_content

    changelog_file.write_text(new_content)
    print(f"✓ Updated debian/changelog (manual)")


def update_appimage_manifest(new_version: str) -> None:
    """Update AppImage manifest/recipe files."""
    project_root = Path(__file__).parent.parent.parent

    # Look for AppImage recipe files
    appimage_files = [
        project_root / "build/appimage/AppImageBuilder.yml",
        project_root / "build/appimage/recipe.yml",
        project_root / "AppImageBuilder.yml",
    ]

    updated = False
    for manifest_file in appimage_files:
        if not manifest_file.exists():
            continue

        content = manifest_file.read_text()
        original = content

        # Update version field
        content = re.sub(
            r'version:\s*["\']?[\d.]+["\']?',
            f'version: "{new_version}"',
            content
        )

        if content != original:
            manifest_file.write_text(content)
            print(f"✓ Updated {manifest_file.name}")
            updated = True

    if not updated:
        print(f"⚠ Skipped AppImage manifests (not found)")


def update_flatpak_manifest(new_version: str) -> None:
    """Update Flatpak manifest files."""
    project_root = Path(__file__).parent.parent.parent

    # Look for Flatpak manifest files
    flatpak_files = [
        project_root / "build/flatpak/com.antidetect.Browser.yml",
        project_root / "build/flatpak/manifest.yml",
        project_root / "com.antidetect.Browser.yml",
    ]

    updated = False
    for manifest_file in flatpak_files:
        if not manifest_file.exists():
            continue

        content = manifest_file.read_text()
        original = content

        # Update version in tag or branch fields
        content = re.sub(
            r'(tag|branch):\s*["\']?v?[\d.]+["\']?',
            f'tag: "v{new_version}"',
            content
        )

        if content != original:
            manifest_file.write_text(content)
            print(f"✓ Updated {manifest_file.name}")
            updated = True

    if not updated:
        print(f"⚠ Skipped Flatpak manifests (not found)")


def main() -> None:
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python bump_version.py 0.2.0")
        print("  python bump_version.py --major")
        print("  python bump_version.py --minor")
        print("  python bump_version.py --patch")
        sys.exit(1)

    arg = sys.argv[1]
    current_version = get_current_version()

    if arg.startswith("--"):
        part = arg[2:]
        if part not in ["major", "minor", "patch"]:
            print(f"Error: Invalid part '{part}'. Use major, minor, or patch.")
            sys.exit(1)
        new_version = increment_version(current_version, part)
    else:
        new_version = arg
        # Validate version format
        try:
            parse_version(new_version)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    print(f"\nBumping version: {current_version} → {new_version}\n")

    # Update all files (Windows + Linux)
    print("Updating cross-platform files:")
    update_pyproject_toml(new_version)
    update_github_workflows(new_version)

    print("\nUpdating Windows files:")
    update_version_info(new_version)
    update_inno_setup(new_version)
    update_updater_py(new_version)

    print("\nUpdating Linux files:")
    update_debian_changelog(new_version)
    update_appimage_manifest(new_version)
    update_flatpak_manifest(new_version)

    print(f"\n✅ Version bumped to {new_version}")
    print("\nNext steps:")
    print(f"  1. Review changes: git diff")
    print(f"  2. Commit: git commit -am 'Bump version to {new_version}'")
    print(f"  3. Tag: git tag v{new_version}")
    print(f"  4. Push: git push && git push --tags")

    print("\nPlatform-specific notes:")
    print("  Windows: Version info, installer, and updater updated")
    print("  Linux: Debian changelog, AppImage, and Flatpak updated")
    print("  CI/CD: GitHub workflows updated")


if __name__ == "__main__":
    main()
