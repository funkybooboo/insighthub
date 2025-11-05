.PHONY: install test format lint type-check check clean run help

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install --no-root

test:  ## Run tests with coverage
	poetry run pytest tests/ -v --cov=src --cov-report=term-missing

format:  ## Format code with black and isort
	poetry run black src tests
	poetry run isort src tests
	poetry run ruff check src tests --fix

lint:  ## Run ruff linter
	poetry run ruff check src tests

type-check:  ## Run mypy type checker
	poetry run mypy src tests

check: format lint type-check test  ## Run all checks (format, lint, type-check, test)

clean:  ## Clean generated files
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run the hello world program
	poetry run python src/hello.py
