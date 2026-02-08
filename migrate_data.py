#!/usr/bin/env python3
"""Migrate data from old location (./data) to platform-specific location."""

import shutil
import sys
from pathlib import Path


def get_old_data_dir() -> Path:
    """Get old data directory location (./data)."""
    # Assuming script is in project root or being run from there
    return Path("data").resolve()


def get_new_data_dir() -> Path:
    """Get new platform-specific data directory."""
    # Import paths module
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from antidetect_playwright.gui.paths import get_data_dir
    return get_data_dir()


def migrate_data():
    """Migrate data from old location to new location."""
    old_dir = get_old_data_dir()
    new_dir = get_new_data_dir()

    print(f"Migration Tool - Antidetect Browser")
    print(f"=" * 60)
    print(f"Old data location: {old_dir}")
    print(f"New data location: {new_dir}")
    print(f"=" * 60)

    # Check if old directory exists
    if not old_dir.exists():
        print(f"\n❌ Old data directory not found: {old_dir}")
        print("Nothing to migrate.")
        return 0

    # Check if old directory has data
    if not any(old_dir.iterdir()):
        print(f"\n⚠️  Old data directory is empty: {old_dir}")
        print("Nothing to migrate.")
        return 0

    # Check if new directory already has data
    if new_dir.exists() and any(new_dir.iterdir()):
        print(f"\n⚠️  New data directory already contains data: {new_dir}")
        response = input("Overwrite existing data? This cannot be undone. (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            return 1

    print(f"\n📦 Migrating data...")

    try:
        # Create new directory if it doesn't exist
        new_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files and directories
        for item in old_dir.iterdir():
            source = item
            destination = new_dir / item.name

            if item.is_file():
                print(f"  Copying file: {item.name}")
                shutil.copy2(source, destination)
            elif item.is_dir():
                print(f"  Copying directory: {item.name}/")
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)

        print(f"\n✅ Migration completed successfully!")
        print(f"\nYour data is now at: {new_dir}")
        print(f"\nOld data directory ({old_dir}) is still intact.")
        print(f"You can safely delete it after verifying everything works.")

        # Offer to delete old directory
        response = input(f"\nDelete old data directory? (yes/no): ")
        if response.lower() == "yes":
            shutil.rmtree(old_dir)
            print(f"✅ Old data directory deleted: {old_dir}")
        else:
            print(f"Old data directory kept at: {old_dir}")

        return 0

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"Your old data at {old_dir} is still intact.")
        return 1


if __name__ == "__main__":
    sys.exit(migrate_data())
