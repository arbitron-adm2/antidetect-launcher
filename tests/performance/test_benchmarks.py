"""Performance benchmark tests."""

import pytest
import asyncio
import time
from datetime import datetime


@pytest.mark.performance
@pytest.mark.asyncio
class TestBrowserPoolPerformance:
    """Test browser pool performance."""

    async def test_context_creation_speed(self, browser_pool, mock_browser_profile, performance_monitor):
        """Benchmark context creation speed."""
        performance_monitor.start()

        contexts = []
        for _ in range(5):
            async with browser_pool.acquire_context(mock_browser_profile) as ctx:
                contexts.append(ctx)
                await asyncio.sleep(0.1)

        performance_monitor.stop()

        assert performance_monitor.elapsed < 10.0  # Should complete in 10 seconds
        print(f"Context creation: {performance_monitor.elapsed:.2f}s")

    async def test_page_load_performance(self, browser_pool, mock_browser_profile, performance_monitor):
        """Benchmark page load performance."""
        performance_monitor.start()

        async with browser_pool.acquire_page(mock_browser_profile) as page:
            await page.goto("about:blank")

        performance_monitor.stop()

        assert performance_monitor.elapsed < 5.0  # Should load quickly
        print(f"Page load: {performance_monitor.elapsed:.2f}s")

    async def test_concurrent_contexts(self, browser_pool, mock_fingerprint, performance_monitor):
        """Benchmark concurrent context handling."""
        from antidetect_playwright.domain.models import BrowserProfile

        profiles = [
            BrowserProfile(
                id=f"perf-{i}",
                fingerprint=mock_fingerprint,
                proxy=None,
                storage_path=f"/tmp/perf-{i}",
                created_at=datetime.now(),
            )
            for i in range(3)
        ]

        performance_monitor.start()

        tasks = []
        for profile in profiles:
            async def navigate(p):
                async with browser_pool.acquire_page(p) as page:
                    await page.goto("about:blank")

            tasks.append(navigate(profile))

        await asyncio.gather(*tasks)

        performance_monitor.stop()

        assert performance_monitor.elapsed < 15.0
        print(f"Concurrent contexts: {performance_monitor.elapsed:.2f}s")


@pytest.mark.performance
class TestStoragePerformance:
    """Test storage performance."""

    def test_bulk_profile_save(self, mock_storage, performance_monitor):
        """Benchmark bulk profile saving."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        profiles = [
            BrowserProfile(
                id=f"bulk-{i}",
                name=f"Bulk {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
            )
            for i in range(100)
        ]

        performance_monitor.start()

        for profile in profiles:
            mock_storage.save_profile(profile)

        performance_monitor.stop()

        assert performance_monitor.elapsed < 5.0
        print(f"Bulk save 100 profiles: {performance_monitor.elapsed:.2f}s")

    def test_profile_retrieval_speed(self, mock_storage, performance_monitor):
        """Benchmark profile retrieval."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        # Create test data
        profiles = [
            BrowserProfile(
                id=f"retrieve-{i}",
                name=f"Retrieve {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
            )
            for i in range(100)
        ]

        for profile in profiles:
            mock_storage.save_profile(profile)

        performance_monitor.start()

        for i in range(100):
            mock_storage.get_profile(f"retrieve-{i}")

        performance_monitor.stop()

        assert performance_monitor.elapsed < 2.0
        print(f"Retrieve 100 profiles: {performance_monitor.elapsed:.2f}s")

    def test_list_profiles_performance(self, mock_storage, performance_monitor):
        """Benchmark listing profiles."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        # Create test data
        for i in range(200):
            profile = BrowserProfile(
                id=f"list-{i}",
                name=f"List {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
            )
            mock_storage.save_profile(profile)

        performance_monitor.start()

        profiles = mock_storage.list_profiles()

        performance_monitor.stop()

        assert len(profiles) == 200
        assert performance_monitor.elapsed < 1.0
        print(f"List 200 profiles: {performance_monitor.elapsed:.2f}s")


@pytest.mark.performance
class TestFingerprintGenerationPerformance:
    """Test fingerprint generation performance."""

    def test_fingerprint_generation_speed(self, performance_monitor):
        """Benchmark fingerprint generation."""
        from antidetect_playwright.fingerprint.generator import FingerprintGenerator

        generator = FingerprintGenerator()

        performance_monitor.start()

        fingerprints = [generator.generate() for _ in range(100)]

        performance_monitor.stop()

        assert len(fingerprints) == 100
        assert performance_monitor.elapsed < 5.0
        print(f"Generate 100 fingerprints: {performance_monitor.elapsed:.2f}s")

    def test_fingerprint_uniqueness_check(self):
        """Test fingerprint uniqueness across many generations."""
        from antidetect_playwright.fingerprint.generator import FingerprintGenerator

        generator = FingerprintGenerator()
        fingerprints = [generator.generate() for _ in range(50)]

        # Check canvas noise variation
        canvas_noises = [fp.canvas_noise for fp in fingerprints]
        unique_noises = len(set(canvas_noises))

        # Should have good variation
        assert unique_noises > 40


@pytest.mark.performance
@pytest.mark.asyncio
class TestMemoryUsage:
    """Test memory usage patterns."""

    async def test_context_memory_cleanup(self, browser_pool, mock_browser_profile):
        """Test contexts are properly cleaned up."""
        import gc

        initial_count = await browser_pool.get_active_contexts_count()

        # Create and destroy contexts
        for _ in range(5):
            async with browser_pool.acquire_context(mock_browser_profile):
                pass

        gc.collect()
        await asyncio.sleep(0.1)

        final_count = await browser_pool.get_active_contexts_count()
        assert final_count == initial_count

    async def test_page_memory_cleanup(self, browser_pool, mock_browser_profile):
        """Test pages are properly cleaned up."""
        import gc

        # Create and destroy pages
        for _ in range(10):
            async with browser_pool.acquire_page(mock_browser_profile) as page:
                await page.goto("about:blank")

        gc.collect()

        # Should not leak memory
        # In real test, would check actual memory usage


@pytest.mark.performance
class TestConcurrencyLimits:
    """Test concurrency limits."""

    @pytest.mark.asyncio
    async def test_max_contexts_enforcement(self, browser_pool, mock_browser_profile):
        """Test max contexts limit is enforced."""
        max_contexts = await browser_pool.get_max_contexts()

        # Try to acquire more than max
        contexts = []
        semaphore_tasks = []

        async def acquire():
            async with browser_pool.acquire_context(mock_browser_profile) as ctx:
                contexts.append(ctx)
                await asyncio.sleep(1)

        # Start max_contexts + 2 tasks
        tasks = [asyncio.create_task(acquire()) for _ in range(max_contexts + 2)]

        # Give some time for contexts to be acquired
        await asyncio.sleep(0.5)

        # Active count should not exceed max
        active = await browser_pool.get_active_contexts_count()
        assert active <= max_contexts

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)
