"""Cross-platform compatibility tests."""

import pytest
import sys
import platform


@pytest.mark.unit
class TestPlatformDetection:
    """Test platform detection."""

    def test_current_platform(self):
        """Test platform can be detected."""
        system = platform.system()
        assert system in ["Linux", "Windows", "Darwin"]

    def test_python_version(self):
        """Test Python version is 3.12+."""
        assert sys.version_info >= (3, 12)


@pytest.mark.integration
class TestCrossPlatformPaths:
    """Test path handling across platforms."""

    def test_path_creation(self, temp_dir):
        """Test path creation works on all platforms."""
        from pathlib import Path

        test_path = temp_dir / "test" / "nested" / "path"
        test_path.mkdir(parents=True, exist_ok=True)

        assert test_path.exists()
        assert test_path.is_dir()

    def test_path_separators(self, temp_dir):
        """Test path separators are handled correctly."""
        from pathlib import Path

        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        assert test_file.exists()

    def test_storage_paths(self, mock_storage):
        """Test storage handles paths correctly."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus
        from datetime import datetime

        profile = BrowserProfile(
            id="path-test",
            name="Path Test",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
        )

        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("path-test")

        assert loaded.id == "path-test"


@pytest.mark.integration
@pytest.mark.gui
class TestGUICrossPlatform:
    """Test GUI works across platforms."""

    @pytest.fixture
    def qapp(self):
        """Create QApplication."""
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    def test_qapplication_creation(self, qapp):
        """Test QApplication can be created."""
        assert qapp is not None

    def test_widget_creation(self, qapp):
        """Test widgets can be created."""
        from PyQt6.QtWidgets import QWidget

        widget = QWidget()
        assert widget is not None

    @pytest.mark.skipif(
        platform.system() == "Linux" and not os.environ.get("DISPLAY"),
        reason="No display available on Linux",
    )
    def test_window_creation(self, qapp):
        """Test windows can be created."""
        from PyQt6.QtWidgets import QMainWindow

        window = QMainWindow()
        assert window is not None


@pytest.mark.asyncio
class TestBrowserCrossPlatform:
    """Test browser works across platforms."""

    async def test_browser_launch(self, browser_pool):
        """Test browser can launch on current platform."""
        assert browser_pool is not None
        max_contexts = await browser_pool.get_max_contexts()
        assert max_contexts > 0

    async def test_page_creation(self, browser_pool, mock_browser_profile):
        """Test page can be created on current platform."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")
            assert page.url == "about:blank"


import os


@pytest.mark.integration
class TestFileSystemOperations:
    """Test file system operations across platforms."""

    def test_temp_directory(self, temp_dir):
        """Test temporary directory creation."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_file_write_read(self, temp_dir):
        """Test file write and read."""
        test_file = temp_dir / "test.txt"
        content = "Test content"

        test_file.write_text(content)
        read_content = test_file.read_text()

        assert read_content == content

    def test_directory_listing(self, temp_dir):
        """Test directory listing."""
        (temp_dir / "file1.txt").write_text("1")
        (temp_dir / "file2.txt").write_text("2")

        files = list(temp_dir.glob("*.txt"))
        assert len(files) == 2


@pytest.mark.unit
class TestEncodingHandling:
    """Test encoding is handled correctly across platforms."""

    def test_unicode_in_profiles(self, mock_storage):
        """Test Unicode handling in profiles."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus
        from datetime import datetime

        profile = BrowserProfile(
            id="unicode-test",
            name="Test 测试 テスト",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            notes="Привет мир 你好世界 こんにちは",
        )

        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("unicode-test")

        assert loaded.name == "Test 测试 テスト"
        assert loaded.notes == "Привет мир 你好世界 こんにちは"

    def test_special_characters(self, temp_dir):
        """Test special characters in file content."""
        test_file = temp_dir / "special.txt"
        content = "Special: @#$%^&*(){}[]|\\/<>?"

        test_file.write_text(content, encoding="utf-8")
        read_content = test_file.read_text(encoding="utf-8")

        assert read_content == content
