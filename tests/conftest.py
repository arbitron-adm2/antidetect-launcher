"""Pytest configuration and shared fixtures."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from antidetect_playwright.config import AppConfig
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
from antidetect_playwright.gui.models import BrowserProfile as GUIProfile
from antidetect_playwright.gui.models import ProfileStatus
from antidetect_playwright.gui.storage import Storage
from antidetect_playwright.infrastructure.browser import BrowserPool


# Test configuration
@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for async tests."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir: Path) -> AppConfig:
    """Create mock application config."""
    return AppConfig(
        browser_type="chromium",
        headless=True,
        max_contexts=5,
        context_timeout=30,
        page_timeout=30,
        storage_path=str(temp_dir / "profiles"),
        executable_path="",
        stealth_enabled=True,
        redis_url="redis://localhost:6379/0",
    )


@pytest.fixture
def mock_fingerprint() -> Fingerprint:
    """Create mock fingerprint."""
    return Fingerprint(
        id="test-fingerprint-1",
        navigator=NavigatorConfig(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            language="en-US",
            languages=("en-US", "en"),
            platform="Win32",
            hardware_concurrency=8,
            device_memory=8,
            max_touch_points=0,
            vendor="Google Inc.",
        ),
        screen=ScreenResolution(
            width=1920,
            height=1080,
        ),
        timezone="America/New_York",
        webgl=WebGLConfig(
            vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            unmasked_vendor="Intel Inc.",
            unmasked_renderer="Intel Iris OpenGL Engine",
        ),
        canvas=CanvasConfig(
            noise_r=0.1,
            noise_g=0.1,
            noise_b=0.1,
            noise_a=0.1,
        ),
        audio=AudioConfig(
            sample_rate=44100,
            noise_factor=0.1,
        ),
        fonts=("Arial", "Times New Roman", "Courier New"),
        plugins=("Chrome PDF Plugin", "Native Client"),
    )


@pytest.fixture
def mock_proxy() -> ProxyConfig:
    """Create mock proxy config."""
    return ProxyConfig(
        server="127.0.0.1:8080",
        username="user",
        password="pass",
        protocol="http",
    )


@pytest.fixture
def mock_browser_profile(
    mock_fingerprint: Fingerprint, mock_proxy: ProxyConfig, temp_dir: Path
) -> BrowserProfile:
    """Create mock browser profile."""
    from datetime import datetime

    return BrowserProfile(
        id="test-profile-1",
        fingerprint=mock_fingerprint,
        proxy=mock_proxy,
        storage_path=str(temp_dir / "profile-1"),
        created_at=datetime.now(),
        last_used_at=None,
    )


@pytest.fixture
def mock_gui_profile() -> GUIProfile:
    """Create mock GUI profile."""
    from datetime import datetime

    return GUIProfile(
        id="gui-profile-1",
        name="Test Profile",
        status=ProfileStatus.READY,
        proxy="http://127.0.0.1:8080",
        user_agent="Mozilla/5.0 Test",
        created_at=datetime.now(),
        folder="Test Folder",
        tags=["test", "automation"],
        notes="Test notes",
    )


@pytest.fixture
def mock_storage(temp_dir: Path) -> Storage:
    """Create mock storage instance."""
    storage = Storage(str(temp_dir / "storage"))
    return storage


# Browser fixtures
@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Shared browser instance for tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Create new browser context."""
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Create new page."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
async def browser_pool(mock_config: AppConfig) -> AsyncGenerator[BrowserPool, None]:
    """Create browser pool instance."""
    pool = BrowserPool(
        browser_type=mock_config.browser_type,
        max_contexts=mock_config.max_contexts,
        context_timeout=mock_config.context_timeout,
        page_timeout=mock_config.page_timeout,
        headless=mock_config.headless,
        executable_path=mock_config.executable_path,
        stealth_enabled=mock_config.stealth_enabled,
    )
    await pool.initialize()
    yield pool
    await pool.shutdown()


# Mock fixtures
@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.keys = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_playwright():
    """Mock Playwright instance."""
    mock = MagicMock()
    mock.chromium = MagicMock()
    mock.firefox = MagicMock()
    mock.webkit = MagicMock()
    return mock


# Performance monitoring
@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.memory_start = None
            self.memory_end = None

        def start(self):
            self.start_time = time.perf_counter()
            try:
                import psutil

                process = psutil.Process()
                self.memory_start = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                self.memory_start = None

        def stop(self):
            self.end_time = time.perf_counter()
            try:
                import psutil

                process = psutil.Process()
                self.memory_end = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                self.memory_end = None

        @property
        def elapsed(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

        @property
        def memory_delta(self) -> float:
            if self.memory_start is not None and self.memory_end is not None:
                return self.memory_end - self.memory_start
            return 0.0

    return PerformanceMonitor()


# Markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "stress: Stress tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "gui: GUI tests requiring display")
    config.addinivalue_line("markers", "network: Tests requiring network access")
