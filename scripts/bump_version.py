#!/usr/bin/env python3
"""Bump project version."""

import re
import sys
from pathlib import Path


def bump_version(current_version, bump_type):
    """Bump version number."""
    major, minor, patch = map(int, current_version.split("."))

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()

    # Update version line
    new_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )

    pyproject_path.write_text(new_content)
    print(f"Updated pyproject.toml: {new_version}")


def update_spec_file(new_version):
    """Update version in .spec file."""
    spec_path = Path(__file__).parent.parent / "antidetect-browser.spec"
    if not spec_path.exists():
        return

    content = spec_path.read_text()
    new_content = re.sub(
        r"'CFBundleVersion': '[^']+'",
        f"'CFBundleVersion': '{new_version}'",
        content
    )
    new_content = re.sub(
        r"'CFBundleShortVersionString': '[^']+'",
        f"'CFBundleShortVersionString': '{new_version}'",
        new_content
    )

    spec_path.write_text(new_content)
    print(f"Updated antidetect-browser.spec: {new_version}")


def get_current_version():
    """Get current version from pyproject.toml."""
    import tomllib
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: bump_version.py [major|minor|patch|VERSION]")
        print("\nExamples:")
        print("  python scripts/bump_version.py patch   # 0.1.0 -> 0.1.1")
        print("  python scripts/bump_version.py minor   # 0.1.0 -> 0.2.0")
        print("  python scripts/bump_version.py major   # 0.1.0 -> 1.0.0")
        print("  python scripts/bump_version.py 1.2.3   # Set to 1.2.3")
        sys.exit(1)

    arg = sys.argv[1]
    current_version = get_current_version()

    if arg in ["major", "minor", "patch"]:
        new_version = bump_version(current_version, arg)
    else:
        # Manual version
        if not re.match(r'^\d+\.\d+\.\d+$', arg):
            print(f"ERROR: Invalid version format: {arg}")
            print("Version must be in format: MAJOR.MINOR.PATCH (e.g., 1.2.3)")
            sys.exit(1)
        new_version = arg

    print(f"Bumping version: {current_version} -> {new_version}")

    # Update files
    update_pyproject_toml(new_version)
    update_spec_file(new_version)

    print("\nVersion bumped successfully!")
    print(f"\nNext steps:")
    print(f"  1. Review changes: git diff")
    print(f"  2. Commit: git commit -am 'Bump version to {new_version}'")
    print(f"  3. Tag: git tag -a v{new_version} -m 'Release v{new_version}'")
    print(f"  4. Push: git push && git push --tags")


if __name__ == "__main__":
    main()
