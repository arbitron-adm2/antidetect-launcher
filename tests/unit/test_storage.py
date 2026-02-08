"""Unit tests for storage layer."""

import pytest
from datetime import datetime
from pathlib import Path

from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus
from antidetect_playwright.gui.storage import Storage, StorageError, ProfileNotFoundError


@pytest.mark.unit
class TestStorage:
    """Test storage implementation."""

    def test_storage_creation(self, temp_dir: Path):
        """Test storage can be created."""
        storage = Storage(str(temp_dir))
        assert storage is not None

    def test_save_profile(self, mock_storage: Storage, mock_gui_profile: BrowserProfile):
        """Test saving a profile."""
        mock_storage.save_profile(mock_gui_profile)
        loaded = mock_storage.get_profile(mock_gui_profile.id)
        assert loaded.id == mock_gui_profile.id
        assert loaded.name == mock_gui_profile.name

    def test_get_nonexistent_profile(self, mock_storage: Storage):
        """Test getting non-existent profile raises error."""
        with pytest.raises(ProfileNotFoundError):
            mock_storage.get_profile("nonexistent-id")

    def test_delete_profile(self, mock_storage: Storage, mock_gui_profile: BrowserProfile):
        """Test deleting a profile."""
        mock_storage.save_profile(mock_gui_profile)
        mock_storage.delete_profile(mock_gui_profile.id)
        with pytest.raises(ProfileNotFoundError):
            mock_storage.get_profile(mock_gui_profile.id)

    def test_list_profiles(self, mock_storage: Storage):
        """Test listing all profiles."""
        profile1 = BrowserProfile(
            id="p1",
            name="Profile 1",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
        )
        profile2 = BrowserProfile(
            id="p2",
            name="Profile 2",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
        )
        mock_storage.save_profile(profile1)
        mock_storage.save_profile(profile2)

        profiles = mock_storage.list_profiles()
        assert len(profiles) == 2
        assert any(p.id == "p1" for p in profiles)
        assert any(p.id == "p2" for p in profiles)

    def test_update_profile(self, mock_storage: Storage, mock_gui_profile: BrowserProfile):
        """Test updating a profile."""
        mock_storage.save_profile(mock_gui_profile)
        mock_gui_profile.name = "Updated Name"
        mock_storage.save_profile(mock_gui_profile)

        loaded = mock_storage.get_profile(mock_gui_profile.id)
        assert loaded.name == "Updated Name"

    def test_profile_with_tags(self, mock_storage: Storage):
        """Test profile with tags."""
        profile = BrowserProfile(
            id="tagged",
            name="Tagged Profile",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            tags=["tag1", "tag2"],
        )
        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("tagged")
        assert len(loaded.tags) == 2
        assert "tag1" in loaded.tags

    def test_profile_with_folder(self, mock_storage: Storage):
        """Test profile with folder."""
        profile = BrowserProfile(
            id="folder-test",
            name="Folder Profile",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            folder="Work",
        )
        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("folder-test")
        assert loaded.folder == "Work"

    def test_list_folders(self, mock_storage: Storage):
        """Test listing folders."""
        p1 = BrowserProfile(
            id="p1", name="P1", status=ProfileStatus.READY, created_at=datetime.now(), folder="F1"
        )
        p2 = BrowserProfile(
            id="p2", name="P2", status=ProfileStatus.READY, created_at=datetime.now(), folder="F2"
        )
        mock_storage.save_profile(p1)
        mock_storage.save_profile(p2)

        folders = mock_storage.list_folders()
        assert "F1" in folders
        assert "F2" in folders

    def test_list_tags(self, mock_storage: Storage):
        """Test listing tags."""
        p1 = BrowserProfile(
            id="p1",
            name="P1",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            tags=["t1", "t2"],
        )
        p2 = BrowserProfile(
            id="p2",
            name="P2",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            tags=["t2", "t3"],
        )
        mock_storage.save_profile(p1)
        mock_storage.save_profile(p2)

        tags = mock_storage.list_tags()
        assert "t1" in tags
        assert "t2" in tags
        assert "t3" in tags


@pytest.mark.unit
class TestStorageSettings:
    """Test storage settings."""

    def test_get_settings(self, mock_storage: Storage):
        """Test getting settings."""
        settings = mock_storage.get_settings()
        assert settings is not None

    def test_save_settings(self, mock_storage: Storage):
        """Test saving settings."""
        settings = mock_storage.get_settings()
        settings.window_width = 1600
        mock_storage.save_settings(settings)

        loaded = mock_storage.get_settings()
        assert loaded.window_width == 1600
