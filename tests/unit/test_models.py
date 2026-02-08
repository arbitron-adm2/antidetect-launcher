"""Unit tests for domain models."""

import pytest
from datetime import datetime

from antidetect_playwright.domain.models import (
    BrowserProfile,
    Fingerprint,
    NavigatorConfig,
    ProxyConfig,
    ScreenResolution,
    WebGLConfig,
    CanvasConfig,
    AudioConfig,
)


@pytest.mark.unit
class TestFingerprint:
    """Test Fingerprint model."""

    def test_fingerprint_creation(self, mock_fingerprint: Fingerprint):
        """Test fingerprint can be created."""
        assert mock_fingerprint.navigator.user_agent
        assert mock_fingerprint.screen.width > 0
        assert mock_fingerprint.timezone

    def test_to_injection_data(self, mock_fingerprint: Fingerprint):
        """Test fingerprint conversion to injection data."""
        data = mock_fingerprint.to_injection_data()
        assert "navigator" in data
        assert "screen" in data
        assert data["navigator"]["userAgent"] == mock_fingerprint.navigator.user_agent
        assert data["screen"]["width"] == mock_fingerprint.screen.width

    def test_canvas_noise_range(self, mock_fingerprint: Fingerprint):
        """Test canvas noise is within valid range."""
        assert -1.0 <= mock_fingerprint.canvas.noise_r <= 1.0
        assert -1.0 <= mock_fingerprint.canvas.noise_g <= 1.0

    def test_audio_noise_range(self, mock_fingerprint: Fingerprint):
        """Test audio noise is within valid range."""
        assert 0.0 <= mock_fingerprint.audio.noise_factor <= 1.0


@pytest.mark.unit
class TestProxyConfig:
    """Test ProxyConfig model."""

    def test_proxy_creation(self, mock_proxy: ProxyConfig):
        """Test proxy config can be created."""
        assert mock_proxy.server
        assert mock_proxy.protocol in ["http", "https", "socks5"]

    def test_to_playwright_proxy(self, mock_proxy: ProxyConfig):
        """Test conversion to Playwright proxy format."""
        playwright_proxy = mock_proxy.to_playwright_proxy()
        assert "server" in playwright_proxy
        assert playwright_proxy["server"] == f"{mock_proxy.protocol}://{mock_proxy.server}"

    def test_proxy_with_credentials(self):
        """Test proxy with authentication."""
        proxy = ProxyConfig(
            server="127.0.0.1:8080",
            username="testuser",
            password="testpass",
            protocol="http",
        )
        pw_proxy = proxy.to_playwright_proxy()
        assert pw_proxy["username"] == "testuser"
        assert pw_proxy["password"] == "testpass"

    def test_proxy_without_credentials(self):
        """Test proxy without authentication."""
        proxy = ProxyConfig(server="127.0.0.1:8080", protocol="http")
        pw_proxy = proxy.to_playwright_proxy()
        assert "username" not in pw_proxy
        assert "password" not in pw_proxy


@pytest.mark.unit
class TestBrowserProfile:
    """Test BrowserProfile model."""

    def test_profile_creation(self, mock_browser_profile: BrowserProfile):
        """Test browser profile can be created."""
        assert mock_browser_profile.id
        assert mock_browser_profile.fingerprint
        assert mock_browser_profile.storage_path

    def test_mark_used(self, mock_browser_profile: BrowserProfile):
        """Test marking profile as used."""
        assert mock_browser_profile.last_used_at is None
        mock_browser_profile.mark_used()
        assert mock_browser_profile.last_used_at is not None
        assert isinstance(mock_browser_profile.last_used_at, datetime)

    def test_to_context_options(self, mock_browser_profile: BrowserProfile):
        """Test conversion to Playwright context options."""
        options = mock_browser_profile.to_context_options()
        assert "viewport" in options
        assert "user_agent" in options
        assert "proxy" in options
        assert options["viewport"]["width"] == mock_browser_profile.fingerprint.screen.width
        assert options["user_agent"] == mock_browser_profile.fingerprint.navigator.user_agent

    def test_context_options_viewport(self, mock_browser_profile: BrowserProfile):
        """Test viewport in context options."""
        options = mock_browser_profile.to_context_options()
        assert options["viewport"]["width"] > 0
        assert options["viewport"]["height"] > 0

    def test_context_options_locale(self, mock_browser_profile: BrowserProfile):
        """Test locale in context options."""
        options = mock_browser_profile.to_context_options()
        assert options["locale"] == mock_browser_profile.fingerprint.navigator.language

    def test_cookies_persistence(self, mock_browser_profile: BrowserProfile):
        """Test cookies can be stored in profile."""
        cookies = [
            {"name": "test", "value": "value", "domain": ".example.com", "path": "/"}
        ]
        mock_browser_profile.cookies = cookies
        assert len(mock_browser_profile.cookies) == 1
        assert mock_browser_profile.cookies[0]["name"] == "test"


@pytest.mark.unit
class TestNavigatorConfig:
    """Test NavigatorConfig model."""

    def test_navigator_creation(self):
        """Test navigator data can be created."""
        nav = NavigatorConfig(
            user_agent="Test UA",
            language="en-US",
            languages=("en-US",),
            platform="Win32",
            hardware_concurrency=4,
            device_memory=8,
            max_touch_points=0,
            vendor="Google Inc.",
        )
        assert nav.user_agent == "Test UA"
        assert nav.hardware_concurrency > 0

    def test_hardware_concurrency_positive(self):
        """Test hardware concurrency is positive."""
        nav = NavigatorConfig(
            user_agent="Test",
            language="en",
            languages=("en",),
            platform="Linux",
            hardware_concurrency=8,
            device_memory=16,
            max_touch_points=0,
            vendor="",
        )
        assert nav.hardware_concurrency > 0

    def test_languages_tuple(self):
        """Test languages is a tuple."""
        nav = NavigatorConfig(
            user_agent="Test",
            language="en-US",
            languages=("en-US", "en", "ru"),
            platform="Linux",
            hardware_concurrency=4,
            device_memory=8,
            max_touch_points=0,
            vendor="",
        )
        assert isinstance(nav.languages, tuple)
        assert len(nav.languages) >= 1


@pytest.mark.unit
class TestScreenResolution:
    """Test ScreenResolution model."""

    def test_screen_creation(self):
        """Test screen data can be created."""
        screen = ScreenResolution(
            width=1920,
            height=1080,
        )
        assert screen.width > 0
        assert screen.height > 0

    def test_screen_dimensions_valid(self):
        """Test screen dimensions are valid."""
        screen = ScreenResolution(
            width=1920,
            height=1080,
        )
        assert screen.width > 0
        assert screen.height > 0

    def test_invalid_dimensions(self):
        """Test invalid dimensions raise error."""
        with pytest.raises(ValueError):
            ScreenResolution(width=0, height=1080)

        with pytest.raises(ValueError):
            ScreenResolution(width=1920, height=0)
