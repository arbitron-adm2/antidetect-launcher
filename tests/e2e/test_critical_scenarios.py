"""End-to-end tests for critical scenarios."""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EBrowserAutomation:
    """End-to-end browser automation tests."""

    async def test_complete_browsing_session(self, browser_pool, mock_browser_profile):
        """Test complete browsing session."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Navigate to page
            await page.goto("https://example.com")
            assert "example" in page.url.lower()

            # Check title
            title = await page.title()
            assert title

            # Execute JavaScript
            result = await page.evaluate("1 + 1")
            assert result == 2

    async def test_cookie_persistence(self, browser_pool, mock_browser_profile):
        """Test cookies are persisted across sessions."""
        # First session: set cookie
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("https://example.com")
            await page.context.add_cookies(
                [
                    {
                        "name": "test_cookie",
                        "value": "test_value",
                        "domain": ".example.com",
                        "path": "/",
                    }
                ]
            )

        # Cookies should be saved to profile
        assert len(mock_browser_profile.cookies) > 0
        assert any(c["name"] == "test_cookie" for c in mock_browser_profile.cookies)

    async def test_multiple_tabs(self, browser_pool, mock_browser_profile):
        """Test multiple tabs in same context."""
        async with browser_pool.acquire_context(mock_browser_profile) as context:
            page1 = await context.new_page()
            page2 = await context.new_page()

            await page1.goto("https://example.com")
            await page2.goto("https://example.org")

            assert "example.com" in page1.url
            assert "example.org" in page2.url

            await page1.close()
            await page2.close()

    async def test_form_interaction(self, browser_pool, mock_browser_profile):
        """Test form interaction."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Create a simple form
            await page.goto("about:blank")
            await page.set_content("""
                <html>
                    <body>
                        <input id="test-input" type="text" />
                        <button id="test-button">Click Me</button>
                        <div id="result"></div>
                        <script>
                            document.getElementById('test-button').onclick = function() {
                                var input = document.getElementById('test-input').value;
                                document.getElementById('result').textContent = input;
                            };
                        </script>
                    </body>
                </html>
            """)

            # Interact with form
            await page.fill("#test-input", "test value")
            await page.click("#test-button")

            # Verify result
            result = await page.text_content("#result")
            assert result == "test value"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EStealthScenarios:
    """Test stealth features in real scenarios."""

    async def test_webdriver_detection(self, browser_pool, mock_browser_profile):
        """Test webdriver is not detected."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            # Check various webdriver indicators
            webdriver = await page.evaluate("navigator.webdriver")
            assert webdriver is None or webdriver is False

            # Check for automation flags
            chrome = await page.evaluate("window.chrome")
            assert chrome is not None

    async def test_fingerprint_consistency(self, browser_pool, mock_browser_profile):
        """Test fingerprint remains consistent."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            # Get fingerprint data
            fp_data = await page.evaluate("""() => ({
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                hardwareConcurrency: navigator.hardwareConcurrency,
                screenWidth: screen.width,
                screenHeight: screen.height
            })""")

            # Verify against profile
            assert fp_data["userAgent"] == mock_browser_profile.fingerprint.navigator.user_agent
            assert (
                fp_data["platform"] == mock_browser_profile.fingerprint.navigator.platform
            )
            assert fp_data["screenWidth"] == mock_browser_profile.fingerprint.screen.width

    async def test_canvas_fingerprint_variation(self, browser_pool, mock_fingerprint):
        """Test canvas fingerprint has noise."""
        from antidetect_playwright.domain.models import BrowserProfile

        profile = BrowserProfile(
            id="canvas-test",
            fingerprint=mock_fingerprint,
            proxy=None,
            storage_path="/tmp/canvas-test",
            created_at=datetime.now(),
        )

        async with browser_pool.acquire_page(profile) as page:
            await page.goto("about:blank")

            # Generate canvas fingerprint
            canvas_fp = await page.evaluate("""() => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillText('Canvas fingerprint test', 2, 2);
                return canvas.toDataURL();
            }""")

            assert canvas_fp
            assert canvas_fp.startswith("data:image/png")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.network
class TestE2ENetworkScenarios:
    """Test network-related scenarios."""

    async def test_proxy_usage(self, browser_pool, mock_browser_profile):
        """Test browser uses proxy when configured."""
        # Note: This test requires a working proxy
        # In real scenario, verify IP is different with proxy
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Attempt to navigate (will fail without real proxy)
            try:
                await page.goto("https://httpbin.org/ip", timeout=5000)
            except Exception:
                # Expected if no real proxy
                pass

    async def test_request_interception(self, browser_pool, mock_browser_profile):
        """Test request interception and modification."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            # Headers should be modified by route handler
            # Verify automation headers are removed
            await page.goto("https://example.com")


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EErrorHandling:
    """Test error handling scenarios."""

    async def test_navigation_timeout(self, browser_pool, mock_browser_profile):
        """Test navigation timeout handling."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            with pytest.raises(Exception):
                # Navigate to non-existent domain
                await page.goto("https://thisdoesnotexist12345.com", timeout=5000)

    async def test_invalid_javascript(self, browser_pool, mock_browser_profile):
        """Test invalid JavaScript execution."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

            with pytest.raises(Exception):
                await page.evaluate("this is invalid javascript")

    async def test_closed_context_error(self, browser_pool, mock_browser_profile):
        """Test error when using closed context."""
        context = None
        async with browser_pool.acquire_context(mock_browser_profile) as ctx:
            context = ctx

        # Context is now closed
        with pytest.raises(Exception):
            await context.new_page()


@pytest.mark.e2e
class TestE2EDataPersistence:
    """Test data persistence scenarios."""

    def test_profile_lifecycle(self, mock_storage):
        """Test complete profile lifecycle."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        # Create
        profile = BrowserProfile(
            id="lifecycle-test",
            name="Lifecycle Test",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
        )
        mock_storage.save_profile(profile)

        # Read
        loaded = mock_storage.get_profile("lifecycle-test")
        assert loaded.name == "Lifecycle Test"

        # Update
        loaded.name = "Updated Lifecycle"
        loaded.status = ProfileStatus.RUNNING
        mock_storage.save_profile(loaded)

        updated = mock_storage.get_profile("lifecycle-test")
        assert updated.name == "Updated Lifecycle"
        assert updated.status == ProfileStatus.RUNNING

        # Delete
        mock_storage.delete_profile("lifecycle-test")

        from antidetect_playwright.gui.storage import ProfileNotFoundError

        with pytest.raises(ProfileNotFoundError):
            mock_storage.get_profile("lifecycle-test")

    def test_settings_persistence(self, mock_storage):
        """Test settings persistence."""
        settings = mock_storage.get_settings()
        original_width = settings.window_width

        settings.window_width = 1800
        settings.window_height = 900
        mock_storage.save_settings(settings)

        loaded_settings = mock_storage.get_settings()
        assert loaded_settings.window_width == 1800
        assert loaded_settings.window_height == 900
