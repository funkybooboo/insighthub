.PHONY: help install format lint type-check test clean all

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install all dependencies"
	@echo "  format       - Format code with black and isort"
	@echo "  lint         - Run ruff linter"
	@echo "  type-check   - Run mypy type checker"
	@echo "  check        - Run all checks (format, lint, type-check)"
	@echo "  fix          - Auto-fix formatting and linting issues"
	@echo "  clean        - Remove cache and temporary files"
	@echo "  all          - Run fix and check"

# Install dependencies
install:
	pip install -r requirements.txt

# Format code
format:
	@echo "Running isort..."
	isort src/ --check-only --diff
	@echo "Running black..."
	black src/ --check --diff

# Auto-fix formatting
fix:
	@echo "Fixing imports with isort..."
	isort src/
	@echo "Fixing formatting with black..."
	black src/
	@echo "Fixing linting issues with ruff..."
	ruff check src/ --fix

# Lint code
lint:
	@echo "Running ruff..."
	ruff check src/

# Type check
type-check:
	@echo "Running mypy..."
	mypy src/rag/ --config-file pyproject.toml

# Run all checks
check: format lint type-check
	@echo "All checks passed!"

# Clean temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

# Run fix and then check
all: fix check
	@echo "All done!"
