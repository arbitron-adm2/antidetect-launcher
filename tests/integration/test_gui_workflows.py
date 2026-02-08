"""Integration tests for GUI workflows."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus


@pytest.mark.integration
@pytest.mark.gui
class TestGUIWorkflows:
    """Test GUI integration workflows."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QApplication instance."""
        import sys

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    def test_profile_creation_workflow(self, mock_storage, qapp):
        """Test complete profile creation workflow."""
        profile = BrowserProfile(
            id="workflow-1",
            name="Workflow Test",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            proxy="http://127.0.0.1:8080",
            user_agent="Test UA",
        )

        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("workflow-1")

        assert loaded.id == profile.id
        assert loaded.name == profile.name
        assert loaded.proxy == profile.proxy

    def test_profile_update_workflow(self, mock_storage, qapp):
        """Test profile update workflow."""
        profile = BrowserProfile(
            id="update-1", name="Original", status=ProfileStatus.READY, created_at=datetime.now()
        )
        mock_storage.save_profile(profile)

        profile.name = "Updated"
        profile.tags = ["updated"]
        mock_storage.save_profile(profile)

        loaded = mock_storage.get_profile("update-1")
        assert loaded.name == "Updated"
        assert "updated" in loaded.tags

    def test_profile_delete_workflow(self, mock_storage, qapp):
        """Test profile deletion workflow."""
        profile = BrowserProfile(
            id="delete-1", name="To Delete", status=ProfileStatus.READY, created_at=datetime.now()
        )
        mock_storage.save_profile(profile)

        mock_storage.delete_profile("delete-1")

        from antidetect_playwright.gui.storage import ProfileNotFoundError

        with pytest.raises(ProfileNotFoundError):
            mock_storage.get_profile("delete-1")

    def test_folder_organization_workflow(self, mock_storage, qapp):
        """Test folder organization workflow."""
        profiles = [
            BrowserProfile(
                id=f"folder-{i}",
                name=f"Profile {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
                folder="TestFolder",
            )
            for i in range(3)
        ]

        for profile in profiles:
            mock_storage.save_profile(profile)

        folders = mock_storage.list_folders()
        assert "TestFolder" in folders

        all_profiles = mock_storage.list_profiles()
        folder_profiles = [p for p in all_profiles if p.folder == "TestFolder"]
        assert len(folder_profiles) == 3

    def test_tags_workflow(self, mock_storage, qapp):
        """Test tags workflow."""
        profile = BrowserProfile(
            id="tags-1",
            name="Tagged",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            tags=["work", "testing"],
        )
        mock_storage.save_profile(profile)

        tags = mock_storage.list_tags()
        assert "work" in tags
        assert "testing" in tags


@pytest.mark.integration
class TestBrowserLaunchWorkflow:
    """Test browser launch integration."""

    @pytest.mark.asyncio
    async def test_browser_launch_with_profile(self, browser_pool, mock_browser_profile):
        """Test launching browser with profile."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")
            assert page.url == "about:blank"

    @pytest.mark.asyncio
    async def test_multiple_contexts(self, browser_pool, mock_browser_profile, mock_fingerprint):
        """Test multiple browser contexts."""
        from antidetect_playwright.domain.models import BrowserProfile
        from datetime import datetime
        from pathlib import Path

        profile1 = mock_browser_profile
        profile2 = BrowserProfile(
            id="test-profile-2",
            fingerprint=mock_fingerprint,
            proxy=None,
            storage_path=str(Path("/tmp/profile-2")),
            created_at=datetime.now(),
        )

        async with browser_pool.acquire_context(profile1) as ctx1:
            async with browser_pool.acquire_context(profile2) as ctx2:
                page1 = await ctx1.new_page()
                page2 = await ctx2.new_page()

                await page1.goto("about:blank")
                await page2.goto("about:blank")

                assert page1.url == "about:blank"
                assert page2.url == "about:blank"

                await page1.close()
                await page2.close()


@pytest.mark.integration
@pytest.mark.asyncio
class TestStealthIntegration:
    """Test stealth features integration."""

    async def test_stealth_script_injection(self, browser_pool, mock_browser_profile):
        """Test stealth script is injected."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Check webdriver is hidden
            webdriver = await page.evaluate("navigator.webdriver")
            assert webdriver is None or webdriver is False

    async def test_navigator_properties(self, browser_pool, mock_browser_profile):
        """Test navigator properties match fingerprint."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            user_agent = await page.evaluate("navigator.userAgent")
            assert user_agent == mock_browser_profile.fingerprint.navigator.user_agent

    async def test_screen_properties(self, browser_pool, mock_browser_profile):
        """Test screen properties match fingerprint."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            width = await page.evaluate("screen.width")
            height = await page.evaluate("screen.height")

            assert width == mock_browser_profile.fingerprint.screen.width
            assert height == mock_browser_profile.fingerprint.screen.height


@pytest.mark.integration
class TestStorageIntegration:
    """Test storage integration."""

    def test_concurrent_profile_operations(self, mock_storage):
        """Test concurrent profile operations."""
        profiles = [
            BrowserProfile(
                id=f"concurrent-{i}",
                name=f"Concurrent {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
            )
            for i in range(10)
        ]

        for profile in profiles:
            mock_storage.save_profile(profile)

        loaded_profiles = mock_storage.list_profiles()
        assert len(loaded_profiles) == 10

    def test_profile_search_and_filter(self, mock_storage):
        """Test profile search and filtering."""
        profiles = [
            BrowserProfile(
                id=f"search-{i}",
                name=f"Search Test {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
                folder="Search" if i % 2 == 0 else "Other",
                tags=["even"] if i % 2 == 0 else ["odd"],
            )
            for i in range(10)
        ]

        for profile in profiles:
            mock_storage.save_profile(profile)

        all_profiles = mock_storage.list_profiles()
        search_folder = [p for p in all_profiles if p.folder == "Search"]
        assert len(search_folder) == 5

        even_tagged = [p for p in all_profiles if "even" in p.tags]
        assert len(even_tagged) == 5
