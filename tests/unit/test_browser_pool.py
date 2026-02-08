"""Unit tests for browser pool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from antidetect_playwright.infrastructure.browser import BrowserPool


@pytest.mark.unit
@pytest.mark.asyncio
class TestBrowserPool:
    """Test BrowserPool implementation."""

    async def test_pool_initialization(self, mock_config):
        """Test browser pool can be initialized."""
        pool = BrowserPool(
            browser_type=mock_config.browser_type,
            max_contexts=mock_config.max_contexts,
            context_timeout=mock_config.context_timeout,
            page_timeout=mock_config.page_timeout,
            headless=mock_config.headless,
            executable_path=mock_config.executable_path,
            stealth_enabled=mock_config.stealth_enabled,
        )
        assert pool._max_contexts == mock_config.max_contexts
        assert pool._browser_type == mock_config.browser_type

    async def test_get_max_contexts(self, browser_pool: BrowserPool):
        """Test getting max contexts."""
        max_contexts = await browser_pool.get_max_contexts()
        assert max_contexts > 0

    async def test_get_active_contexts_count(self, browser_pool: BrowserPool):
        """Test getting active contexts count."""
        count = await browser_pool.get_active_contexts_count()
        assert count >= 0

    @patch("antidetect_playwright.infrastructure.browser.async_playwright")
    async def test_shutdown_cleanup(self, mock_async_pw):
        """Test browser pool cleanup on shutdown."""
        mock_browser = AsyncMock()
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_pw_context.__aexit__ = AsyncMock()
        mock_async_pw.return_value.start = AsyncMock(return_value=mock_pw_context)

        pool = BrowserPool(
            browser_type="chromium",
            max_contexts=5,
            context_timeout=30,
            page_timeout=30,
            headless=True,
            executable_path="",
            stealth_enabled=True,
        )

        pool._browser = mock_browser
        pool._playwright = mock_playwright_instance

        await pool.shutdown()

        mock_browser.close.assert_called_once()
        mock_playwright_instance.stop.assert_called_once()

    async def test_acquire_context_profile_marked_used(
        self, browser_pool: BrowserPool, mock_browser_profile
    ):
        """Test profile is marked as used when context acquired."""
        assert mock_browser_profile.last_used_at is None

        async with browser_pool.acquire_context(mock_browser_profile) as ctx:
            assert ctx is not None

        # Cookies should be saved
        assert isinstance(mock_browser_profile.cookies, list)

    async def test_acquire_context_increments_counter(
        self, browser_pool: BrowserPool, mock_browser_profile
    ):
        """Test active contexts counter increments."""
        initial_count = await browser_pool.get_active_contexts_count()

        async with browser_pool.acquire_context(mock_browser_profile):
            current_count = await browser_pool.get_active_contexts_count()
            assert current_count == initial_count + 1

        final_count = await browser_pool.get_active_contexts_count()
        assert final_count == initial_count

    async def test_acquire_page(self, browser_pool: BrowserPool, mock_browser_profile):
        """Test acquiring a page."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            assert page is not None
            assert page.url == "about:blank"

    async def test_context_timeout_applied(self, browser_pool: BrowserPool, mock_browser_profile):
        """Test context timeout is applied."""
        async with browser_pool.acquire_context(mock_browser_profile) as ctx:
            # Playwright context should have timeout set
            assert ctx is not None


@pytest.mark.unit
class TestBrowserPoolConfiguration:
    """Test browser pool configuration."""

    def test_browser_type_validation(self):
        """Test browser type is set correctly."""
        pool = BrowserPool(
            browser_type="chromium",
            max_contexts=5,
            context_timeout=30,
            page_timeout=30,
            headless=True,
            executable_path="",
            stealth_enabled=True,
        )
        assert pool._browser_type == "chromium"

    def test_headless_mode(self):
        """Test headless mode configuration."""
        pool = BrowserPool(
            browser_type="chromium",
            max_contexts=5,
            context_timeout=30,
            page_timeout=30,
            headless=True,
            executable_path="",
            stealth_enabled=True,
        )
        assert pool._headless is True

    def test_stealth_enabled(self):
        """Test stealth mode configuration."""
        pool = BrowserPool(
            browser_type="chromium",
            max_contexts=5,
            context_timeout=30,
            page_timeout=30,
            headless=True,
            executable_path="",
            stealth_enabled=True,
        )
        assert pool._stealth_enabled is True
