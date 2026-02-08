# Test Suite Documentation

## Overview

Comprehensive test suite for antidetect-playwright with 80%+ code coverage goal.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests for individual components
│   ├── test_models.py
│   ├── test_browser_pool.py
│   ├── test_fingerprint.py
│   └── test_storage.py
├── integration/          # Integration tests for workflows
│   ├── test_gui_workflows.py
│   └── test_cross_platform.py
├── e2e/                  # End-to-end tests
│   └── test_critical_scenarios.py
├── performance/          # Performance benchmarks
│   └── test_benchmarks.py
└── stress/               # Stress tests
    └── test_stress.py
```

## Running Tests

### All Tests
```bash
./scripts/run_tests.sh
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# E2E tests
pytest tests/e2e -v

# Performance tests
pytest tests/performance -v

# Stress tests
pytest tests/stress -v
```

### With Coverage
```bash
pytest tests/ --cov=src/antidetect_playwright --cov-report=html
```

### By Marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip GUI tests (if no display)
pytest -m "not gui"

# Network tests only
pytest -m network
```

## Test Markers

- `unit` - Unit tests (fast, isolated)
- `integration` - Integration tests (moderate speed)
- `e2e` - End-to-end tests (slower)
- `performance` - Performance benchmarks
- `stress` - Stress tests (very slow)
- `slow` - Slow running tests
- `gui` - Tests requiring GUI/display
- `network` - Tests requiring network access

## Coverage Goals

- **Overall**: 80%+
- **Core modules**: 90%+
- **GUI modules**: 70%+
- **Infrastructure**: 85%+

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Nightly builds (stress tests)

### GitHub Actions Workflow

- Unit tests on Linux, Windows, macOS
- Integration tests on Linux, Windows
- E2E tests on Linux
- Coverage reports uploaded to Codecov
- Performance benchmarks archived

## Writing Tests

### Unit Test Example
```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    def test_feature(self):
        assert True
```

### Async Test Example
```python
import pytest

@pytest.mark.asyncio
async def test_async_feature(browser_pool):
    async with browser_pool.acquire_page(profile) as page:
        await page.goto("about:blank")
        assert page.url == "about:blank"
```

### Using Fixtures
```python
def test_with_storage(mock_storage, mock_gui_profile):
    mock_storage.save_profile(mock_gui_profile)
    loaded = mock_storage.get_profile(mock_gui_profile.id)
    assert loaded.id == mock_gui_profile.id
```

## Available Fixtures

- `temp_dir` - Temporary directory
- `mock_config` - Mock application config
- `mock_fingerprint` - Mock fingerprint
- `mock_proxy` - Mock proxy config
- `mock_browser_profile` - Mock browser profile
- `mock_gui_profile` - Mock GUI profile
- `mock_storage` - Mock storage instance
- `browser_pool` - Real browser pool (async)
- `browser` - Shared browser instance
- `context` - Browser context
- `page` - Browser page
- `performance_monitor` - Performance monitoring

## Performance Testing

Performance tests benchmark:
- Context creation speed
- Page load times
- Concurrent operations
- Memory usage
- Storage operations

Example:
```python
@pytest.mark.performance
async def test_performance(browser_pool, performance_monitor):
    performance_monitor.start()
    # ... test code ...
    performance_monitor.stop()
    assert performance_monitor.elapsed < 5.0
```

## Stress Testing

Stress tests verify:
- Many sequential operations
- Concurrent operations at max capacity
- Memory leak detection
- Error recovery
- Long-running sessions

Example:
```python
@pytest.mark.stress
@pytest.mark.slow
async def test_stress(browser_pool):
    for i in range(100):
        async with browser_pool.acquire_page(profile) as page:
            await page.goto("about:blank")
```

## Cross-Platform Testing

Tests run on:
- Linux (Ubuntu latest)
- Windows (latest)
- macOS (latest)

Platform-specific handling:
- Path separators
- File permissions
- GUI display requirements
- Browser availability

## Debugging Tests

### Run with verbose output
```bash
pytest tests/ -v -s
```

### Run specific test
```bash
pytest tests/unit/test_models.py::TestFingerprint::test_fingerprint_creation -v
```

### Drop into debugger on failure
```bash
pytest tests/ --pdb
```

### Show print statements
```bash
pytest tests/ -s
```

## Coverage Analysis

### Generate HTML report
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Check coverage threshold
```bash
coverage report --fail-under=80
```

### Missing coverage
```bash
coverage report --show-missing
```

## Continuous Improvement

- Add tests for new features
- Maintain 80%+ coverage
- Keep tests fast (< 5min total)
- Fix flaky tests immediately
- Update docs with changes

## Troubleshooting

### Playwright not installed
```bash
playwright install chromium
```

### Import errors
```bash
pip install -e ".[dev]"
```

### GUI tests failing on Linux
```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
```

### Slow tests
```bash
pytest -m "not slow and not stress"
```

## Metrics

Current coverage: Run `./scripts/run_tests.sh` to see latest

Test counts:
- Unit: 50+ tests
- Integration: 20+ tests
- E2E: 15+ tests
- Performance: 10+ tests
- Stress: 15+ tests

Total: 110+ tests
