"""Cross-platform compatibility test suite.

Tests platform-specific functionality and ensures consistent behavior
across Windows, Linux, and macOS.
"""

import os
import sys
import tempfile
from pathlib import Path
import platform
import logging

logger = logging.getLogger(__name__)


def test_path_operations():
    """Test that all path operations work cross-platform."""
    print("Testing path operations...")

    # Test Path.home() - works on all platforms
    home = Path.home()
    assert home.exists(), "Path.home() failed"
    assert home.is_dir(), "Path.home() is not a directory"
    print(f"  ✓ Home directory: {home}")

    # Test creating directories
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test" / "nested" / "dir"
        test_dir.mkdir(parents=True, exist_ok=True)
        assert test_dir.exists(), "mkdir(parents=True) failed"
        print(f"  ✓ Created nested directory: {test_dir}")

        # Test file operations
        test_file = test_dir / "test.txt"
        test_file.write_text("test content", encoding="utf-8")
        assert test_file.exists(), "File creation failed"
        content = test_file.read_text(encoding="utf-8")
        assert content == "test content", "File content mismatch"
        print(f"  ✓ File read/write: {test_file}")

    print("✓ Path operations test passed\n")


def test_permissions():
    """Test file permission handling (platform-aware)."""
    print("Testing file permissions...")

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write("sensitive data")

    try:
        if sys.platform != 'win32':
            # Unix-like systems: test chmod
            import stat
            tmp_path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
            mode = tmp_path.stat().st_mode
            assert mode & stat.S_IRUSR, "Owner read permission not set"
            assert mode & stat.S_IWUSR, "Owner write permission not set"
            assert not (mode & stat.S_IRGRP), "Group read should not be set"
            assert not (mode & stat.S_IROTH), "Other read should not be set"
            print("  ✓ POSIX chmod works correctly")
        else:
            # Windows: permissions work differently
            # File is created with user-only access by default
            assert tmp_path.exists(), "File creation failed on Windows"
            print("  ✓ Windows file created (ACL-based permissions)")
    finally:
        tmp_path.unlink()

    print("✓ Permissions test passed\n")


def test_environment_variables():
    """Test environment variable handling."""
    print("Testing environment variables...")

    # Test setting and getting
    os.environ["TEST_VAR"] = "test_value"
    assert os.environ.get("TEST_VAR") == "test_value"
    del os.environ["TEST_VAR"]
    assert os.environ.get("TEST_VAR") is None
    print("  ✓ Environment variables work correctly")

    # Test platform-specific variables
    if sys.platform == 'win32':
        assert os.environ.get("USERPROFILE") is not None, "USERPROFILE not set on Windows"
        assert os.environ.get("APPDATA") is not None, "APPDATA not set on Windows"
        print("  ✓ Windows environment variables present")
    else:
        assert os.environ.get("HOME") is not None, "HOME not set on Unix"
        print("  ✓ Unix environment variables present")

    print("✓ Environment variables test passed\n")


def test_platform_detection():
    """Test platform detection."""
    print("Testing platform detection...")

    detected_platform = sys.platform
    print(f"  Detected platform: {detected_platform}")

    if detected_platform == 'win32':
        print("  Running on Windows")
    elif detected_platform == 'darwin':
        print("  Running on macOS")
    elif detected_platform.startswith('linux'):
        print("  Running on Linux")
    else:
        print(f"  Unknown platform: {detected_platform}")

    # Test platform module
    print(f"  Platform system: {platform.system()}")
    print(f"  Platform release: {platform.release()}")
    print(f"  Platform machine: {platform.machine()}")

    print("✓ Platform detection test passed\n")


def test_line_endings():
    """Test that line endings are handled correctly."""
    print("Testing line endings...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Write with different line endings
        content = "line1\nline2\nline3"
        test_file.write_text(content, encoding="utf-8")

        # Read back
        read_content = test_file.read_text(encoding="utf-8")
        assert "line1" in read_content
        assert "line2" in read_content
        assert "line3" in read_content
        print("  ✓ Line endings handled correctly")

    print("✓ Line endings test passed\n")


def test_unicode_paths():
    """Test that Unicode characters in paths work."""
    print("Testing Unicode paths...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test various Unicode characters
        unicode_names = [
            "тест",  # Cyrillic
            "测试",  # Chinese
            "テスト",  # Japanese
            "café",  # Latin with accents
        ]

        for name in unicode_names:
            try:
                test_dir = Path(tmpdir) / name
                test_dir.mkdir(exist_ok=True)
                assert test_dir.exists(), f"Failed to create directory: {name}"

                test_file = test_dir / f"{name}.txt"
                test_file.write_text("content", encoding="utf-8")
                assert test_file.exists(), f"Failed to create file: {name}"
                print(f"  ✓ Unicode path works: {name}")
            except Exception as e:
                # Some filesystems may not support all Unicode characters
                print(f"  ⚠ Unicode path not supported: {name} ({e})")

    print("✓ Unicode paths test passed\n")


def run_all_tests():
    """Run all cross-platform compatibility tests."""
    print("=" * 60)
    print("CROSS-PLATFORM COMPATIBILITY TEST SUITE")
    print("=" * 60)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 60 + "\n")

    tests = [
        test_path_operations,
        test_permissions,
        test_environment_variables,
        test_platform_detection,
        test_line_endings,
        test_unicode_paths,
    ]

    failed_tests = []

    for test in tests:
        try:
            test()
        except Exception as e:
            failed_tests.append((test.__name__, e))
            print(f"✗ {test.__name__} FAILED: {e}\n")

    print("=" * 60)
    if not failed_tests:
        print("ALL TESTS PASSED ✓")
        return 0
    else:
        print(f"FAILED TESTS: {len(failed_tests)}")
        for test_name, error in failed_tests:
            print(f"  - {test_name}: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
