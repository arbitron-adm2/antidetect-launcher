#!/usr/bin/env python3
"""Generate update manifest for auto-update system."""

import hashlib
import json
import sys
from pathlib import Path


def calculate_sha256(file_path):
    """Calculate SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size(file_path):
    """Get file size in bytes."""
    return file_path.stat().st_size


def generate_manifest(version):
    """Generate update manifest."""
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"

    manifest = {
        "version": version,
        "release_date": "",  # Will be set by CI
        "release_notes_url": f"https://github.com/antidetect/antidetect-playwright/releases/tag/v{version}",
        "platforms": {}
    }

    # Windows
    windows_exe = list(dist_dir.glob("AntidetectBrowser-Setup-*.exe"))
    if windows_exe:
        exe_file = windows_exe[0]
        manifest["platforms"]["windows"] = {
            "url": f"https://github.com/antidetect/antidetect-playwright/releases/download/v{version}/{exe_file.name}",
            "filename": exe_file.name,
            "size": get_file_size(exe_file),
            "sha256": calculate_sha256(exe_file),
            "type": "installer"
        }

    # Linux
    linux_deb = list(dist_dir.glob("antidetect-browser_*.deb"))
    if linux_deb:
        deb_file = linux_deb[0]
        manifest["platforms"]["linux"] = {
            "url": f"https://github.com/antidetect/antidetect-playwright/releases/download/v{version}/{deb_file.name}",
            "filename": deb_file.name,
            "size": get_file_size(deb_file),
            "sha256": calculate_sha256(deb_file),
            "type": "deb"
        }

    # macOS
    macos_dmg = list(dist_dir.glob("AntidetectBrowser-macOS-*.dmg"))
    if macos_dmg:
        dmg_file = macos_dmg[0]
        manifest["platforms"]["macos"] = {
            "url": f"https://github.com/antidetect/antidetect-playwright/releases/download/v{version}/{dmg_file.name}",
            "filename": dmg_file.name,
            "size": get_file_size(dmg_file),
            "sha256": calculate_sha256(dmg_file),
            "type": "dmg"
        }

    # Save manifest
    manifest_file = dist_dir / "update-manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Update manifest generated: {manifest_file}")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_update_manifest.py VERSION")
        sys.exit(1)

    version = sys.argv[1]
    manifest = generate_manifest(version)
    print(json.dumps(manifest, indent=2))
