.PHONY: install test test-unit test-integration test-watch format lint type-check check clean run help server cli health

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install --no-root

test:  ## Run all tests with coverage
	@echo "Running all tests..."
	poetry run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-unit:  ## Run unit tests only (fast)
	@echo "Running unit tests..."
	poetry run pytest tests/unit/ -v

test-integration:  ## Run integration tests with testcontainers (slower)
	@echo "Running integration tests with testcontainers..."
	@echo "Note: Docker must be running for testcontainers"
	poetry run pytest tests/integration/ -v -s

test-watch:  ## Run tests in watch mode (requires pytest-watch)
	poetry run ptw tests/

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
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run:  ## Run the hello world program
	poetry run python src/hello.py

server:  ## Run Flask API server on port 5000
	poetry run python src/api.py

cli:  ## Run RAG CLI (usage: make cli ARGS="command args")
	poetry run python src/cli.py $(ARGS)

health:  ## Check Flask API server health
	@curl -s http://localhost:5000/health | grep -q "healthy" && echo "Server is healthy" || echo "Server is not responding"
