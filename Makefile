.PHONY: help fix check fix-hard test build clean install format

# Default target
help:
	@echo "Available targets:"
	@echo "  make fix        - Run ruff with safe fixes and format code"
	@echo "  make check      - Run all checks (ruff, mypy, tests)"
	@echo "  make fix-hard   - Run ruff with unsafe fixes"
	@echo "  make test       - Run pytest"
	@echo "  make build      - Build distribution packages"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make install    - Install package in development mode"
	@echo "  make format     - Format code with ruff"

# Fix code with safe fixes and format
fix:
	uv run ruff check . --fix
	uv run ruff format .

# Run all checks - must pass for CI
check:
	@echo "Running ruff check..."
	uv run ruff check .
	@echo "Running ruff format check..."
	uv run ruff format --check .
	@echo "Running mypy..."
	uv run mypy zmk_layout 
	@echo "Running tests..."
	uv run pytest tests/ -v -m "not performance"
	@echo "All checks passed!"

# Fix code with unsafe fixes
fix-hard:
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .

# Run tests only
test:
	uv run pytest tests/ 

# Run performance tests only
test-perf:
	uv run pytest tests/ -v -m "performance"

# Run all tests including performance
test-all:
	uv run pytest tests/ -v --cov=zmk_layout --cov-report=term-missing

# Format code only
format:
	uv run ruff format .

# Build distribution packages
build: clean
	@echo "Building distribution packages..."
	uv build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Install package in development mode
install:
	uv pip install -e ".[dev]"

# Quick check for pre-commit
pre-commit: fix check
	@echo "Pre-commit checks passed!"

# CI/CD target for GitHub Actions
ci: check
	@echo "CI checks completed successfully!"
