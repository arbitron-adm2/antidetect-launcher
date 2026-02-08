"""Unit tests for fingerprint generation."""

import pytest

from antidetect_playwright.fingerprint.generator import FingerprintGenerator
from antidetect_playwright.fingerprint.presets import CHROME_WINDOWS_PRESET


@pytest.mark.unit
class TestFingerprintGenerator:
    """Test fingerprint generator."""

    def test_generator_creation(self):
        """Test generator can be created."""
        generator = FingerprintGenerator()
        assert generator is not None

    def test_generate_fingerprint(self):
        """Test fingerprint generation."""
        generator = FingerprintGenerator()
        fingerprint = generator.generate()
        assert fingerprint.navigator.user_agent
        assert fingerprint.screen.width > 0
        assert fingerprint.timezone

    def test_generate_from_preset(self):
        """Test generation from preset."""
        generator = FingerprintGenerator()
        fingerprint = generator.generate_from_preset(CHROME_WINDOWS_PRESET)
        assert "Windows" in fingerprint.navigator.user_agent
        assert fingerprint.navigator.platform == "Win32"

    def test_fingerprint_uniqueness(self):
        """Test generated fingerprints are unique."""
        generator = FingerprintGenerator()
        fp1 = generator.generate()
        fp2 = generator.generate()
        # Some variation should exist
        assert fp1.canvas_noise != fp2.canvas_noise or fp1.audio_noise != fp2.audio_noise

    def test_consistent_navigator_data(self):
        """Test navigator data is consistent."""
        generator = FingerprintGenerator()
        fingerprint = generator.generate()
        assert fingerprint.navigator.language in fingerprint.navigator.languages

    def test_screen_dimensions_realistic(self):
        """Test screen dimensions are realistic."""
        generator = FingerprintGenerator()
        fingerprint = generator.generate()
        assert 800 <= fingerprint.screen.width <= 7680
        assert 600 <= fingerprint.screen.height <= 4320

    def test_timezone_valid(self):
        """Test timezone is valid."""
        generator = FingerprintGenerator()
        fingerprint = generator.generate()
        assert fingerprint.timezone
        # Common timezone format check
        assert "/" in fingerprint.timezone or fingerprint.timezone.startswith("Etc/")


@pytest.mark.unit
class TestPresets:
    """Test fingerprint presets."""

    def test_chrome_windows_preset(self):
        """Test Chrome Windows preset."""
        assert CHROME_WINDOWS_PRESET["platform"] == "Win32"
        assert "user_agent" in CHROME_WINDOWS_PRESET

    def test_preset_has_required_fields(self):
        """Test preset has all required fields."""
        required_fields = ["platform", "user_agent", "languages"]
        for field in required_fields:
            assert field in CHROME_WINDOWS_PRESET
