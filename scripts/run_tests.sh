#!/bin/bash
# Run comprehensive test suite

set -e

echo "=== Running Antidetect Playwright Test Suite ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Activating .venv..."
    source .venv/bin/activate || source venv/bin/activate || {
        echo -e "${RED}Failed to activate virtual environment${NC}"
        exit 1
    }
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -e ".[dev]" > /dev/null 2>&1
playwright install chromium > /dev/null 2>&1

echo ""
echo "=== 1. Unit Tests ==="
pytest tests/unit -v --cov=src/antidetect_playwright --cov-report=term-missing:skip-covered

echo ""
echo "=== 2. Integration Tests ==="
pytest tests/integration -v -m "not gui" --cov=src/antidetect_playwright --cov-append

echo ""
echo "=== 3. E2E Tests ==="
pytest tests/e2e -v --cov=src/antidetect_playwright --cov-append

echo ""
echo "=== 4. Performance Tests ==="
pytest tests/performance -v --tb=short

echo ""
echo "=== 5. Code Quality ==="
echo "Running ruff..."
ruff check src/

echo "Running mypy..."
mypy src/antidetect_playwright --no-error-summary || true

echo ""
echo "=== Coverage Report ==="
coverage report --precision=2
coverage html

echo ""
echo -e "${GREEN}=== Test Suite Complete ===${NC}"
echo ""
echo "Coverage report generated in htmlcov/"
echo "Open htmlcov/index.html in browser to view detailed coverage"

# Check coverage threshold
COVERAGE=$(coverage report --precision=2 | grep TOTAL | awk '{print $4}' | sed 's/%//')
THRESHOLD=80

if (( $(echo "$COVERAGE >= $THRESHOLD" | bc -l) )); then
    echo -e "${GREEN}✓ Coverage ${COVERAGE}% meets threshold of ${THRESHOLD}%${NC}"
    exit 0
else
    echo -e "${RED}✗ Coverage ${COVERAGE}% below threshold of ${THRESHOLD}%${NC}"
    exit 1
fi
