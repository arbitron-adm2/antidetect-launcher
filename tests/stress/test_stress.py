"""Stress tests for system limits."""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.stress
@pytest.mark.slow
@pytest.mark.asyncio
class TestBrowserStress:
    """Stress test browser operations."""

    async def test_many_sequential_contexts(self, browser_pool, mock_browser_profile):
        """Test creating many contexts sequentially."""
        count = 20

        for i in range(count):
            async with browser_pool.acquire_context(mock_browser_profile) as ctx:
                page = await ctx.new_page()
                await page.goto("about:blank")
                await page.close()

        # Should complete without errors
        active = await browser_pool.get_active_contexts_count()
        assert active == 0

    async def test_rapid_context_creation(self, browser_pool, mock_fingerprint):
        """Test rapid context creation and destruction."""
        from antidetect_playwright.domain.models import BrowserProfile

        async def rapid_acquire(idx):
            profile = BrowserProfile(
                id=f"rapid-{idx}",
                fingerprint=mock_fingerprint,
                proxy=None,
                storage_path=f"/tmp/rapid-{idx}",
                created_at=datetime.now(),
            )
            async with browser_pool.acquire_context(profile):
                await asyncio.sleep(0.1)

        tasks = [rapid_acquire(i) for i in range(10)]
        await asyncio.gather(*tasks)

        active = await browser_pool.get_active_contexts_count()
        assert active == 0

    async def test_long_running_sessions(self, browser_pool, mock_browser_profile):
        """Test long-running browser sessions."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Simulate long session with multiple navigations
            for _ in range(10):
                await page.goto("about:blank")
                await page.evaluate("1 + 1")
                await asyncio.sleep(0.2)

        # Should complete without memory issues


@pytest.mark.stress
@pytest.mark.slow
class TestStorageStress:
    """Stress test storage operations."""

    def test_massive_profile_storage(self, mock_storage):
        """Test storing large number of profiles."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        count = 500

        for i in range(count):
            profile = BrowserProfile(
                id=f"massive-{i}",
                name=f"Massive {i}",
                status=ProfileStatus.READY,
                created_at=datetime.now(),
                tags=[f"tag{i % 10}"],
                folder=f"folder{i % 5}",
            )
            mock_storage.save_profile(profile)

        profiles = mock_storage.list_profiles()
        assert len(profiles) == count

    def test_rapid_updates(self, mock_storage):
        """Test rapid profile updates."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        profile = BrowserProfile(
            id="rapid-update",
            name="Rapid Update",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
        )
        mock_storage.save_profile(profile)

        # Rapid updates
        for i in range(100):
            profile.name = f"Updated {i}"
            mock_storage.save_profile(profile)

        loaded = mock_storage.get_profile("rapid-update")
        assert loaded.name == "Updated 99"

    def test_concurrent_operations(self, mock_storage):
        """Test concurrent storage operations."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus
        import threading

        def save_profiles(start, end):
            for i in range(start, end):
                profile = BrowserProfile(
                    id=f"concurrent-{i}",
                    name=f"Concurrent {i}",
                    status=ProfileStatus.READY,
                    created_at=datetime.now(),
                )
                mock_storage.save_profile(profile)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_profiles, args=(i * 20, (i + 1) * 20))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        profiles = mock_storage.list_profiles()
        assert len(profiles) == 100


@pytest.mark.stress
class TestMemoryStress:
    """Stress test memory usage."""

    def test_large_profile_data(self, mock_storage):
        """Test profiles with large data."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        # Create profile with large notes and many tags
        profile = BrowserProfile(
            id="large-data",
            name="Large Data",
            status=ProfileStatus.READY,
            created_at=datetime.now(),
            notes="A" * 10000,  # Large notes
            tags=[f"tag{i}" for i in range(100)],  # Many tags
        )

        mock_storage.save_profile(profile)
        loaded = mock_storage.get_profile("large-data")

        assert len(loaded.notes) == 10000
        assert len(loaded.tags) == 100

    def test_many_fingerprints_in_memory(self):
        """Test holding many fingerprints in memory."""
        from antidetect_playwright.fingerprint.generator import FingerprintGenerator

        generator = FingerprintGenerator()
        fingerprints = [generator.generate() for _ in range(500)]

        assert len(fingerprints) == 500
        # Memory should not explode


@pytest.mark.stress
@pytest.mark.asyncio
class TestConcurrentBrowserStress:
    """Test concurrent browser operations under stress."""

    async def test_maximum_concurrent_contexts(self, browser_pool, mock_fingerprint):
        """Test maximum concurrent contexts."""
        from antidetect_playwright.domain.models import BrowserProfile

        max_contexts = await browser_pool.get_max_contexts()

        async def use_context(idx):
            profile = BrowserProfile(
                id=f"max-{idx}",
                fingerprint=mock_fingerprint,
                proxy=None,
                storage_path=f"/tmp/max-{idx}",
                created_at=datetime.now(),
            )
            async with browser_pool.acquire_page(profile) as page:
                await page.goto("about:blank")
                await asyncio.sleep(1)

        # Try to use exactly max contexts concurrently
        tasks = [use_context(i) for i in range(max_contexts)]
        await asyncio.gather(*tasks)

        active = await browser_pool.get_active_contexts_count()
        assert active == 0

    async def test_browser_under_load(self, browser_pool, mock_browser_profile):
        """Test browser under continuous load."""
        iterations = 50

        for i in range(iterations):
            async with browser_pool.acquire_page(mock_browser_profile) as page:
                await page.goto("about:blank")
                await page.evaluate(f"console.log('Iteration {i}')")

        # Should handle continuous load
        active = await browser_pool.get_active_contexts_count()
        assert active == 0


@pytest.mark.stress
class TestErrorRecoveryStress:
    """Test error recovery under stress."""

    @pytest.mark.asyncio
    async def test_recover_from_failures(self, browser_pool, mock_browser_profile):
        """Test recovery from multiple failures."""
        success_count = 0
        failure_count = 0

        for i in range(20):
            try:
                async with browser_pool.acquire_page(mock_browser_profile) as page:
                    if i % 5 == 0:
                        # Intentionally cause error
                        await page.goto("https://invalid-url-12345.com", timeout=1000)
                    else:
                        await page.goto("about:blank")
                    success_count += 1
            except Exception:
                failure_count += 1

        # Should have some failures but continue working
        assert failure_count > 0
        assert success_count > 0
        assert success_count + failure_count == 20


@pytest.mark.stress
@pytest.mark.slow
class TestLongRunningStress:
    """Test long-running stress scenarios."""

    @pytest.mark.asyncio
    async def test_extended_session(self, browser_pool, mock_browser_profile):
        """Test extended browsing session."""
        async with browser_pool.acquire_page(mock_browser_profile) as page:
            # Simulate extended usage
            for i in range(30):
                await page.goto("about:blank")
                await page.evaluate(f"localStorage.setItem('test{i}', '{i}')")
                await asyncio.sleep(0.1)

            # Verify data persists
            result = await page.evaluate("localStorage.getItem('test29')")
            assert result == "29"

    def test_storage_endurance(self, mock_storage):
        """Test storage under extended operations."""
        from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus

        # Create, update, delete repeatedly
        for iteration in range(10):
            # Create batch
            for i in range(20):
                profile = BrowserProfile(
                    id=f"endurance-{iteration}-{i}",
                    name=f"Endurance {iteration}-{i}",
                    status=ProfileStatus.READY,
                    created_at=datetime.now(),
                )
                mock_storage.save_profile(profile)

            # Update batch
            for i in range(20):
                profile = mock_storage.get_profile(f"endurance-{iteration}-{i}")
                profile.name = f"Updated {iteration}-{i}"
                mock_storage.save_profile(profile)

            # Delete half
            for i in range(10):
                mock_storage.delete_profile(f"endurance-{iteration}-{i}")

        # Should still be operational
        profiles = mock_storage.list_profiles()
        assert len(profiles) == 100  # 10 iterations * 10 remaining
