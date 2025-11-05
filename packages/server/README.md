# InsightHub Server

Python backend for the InsightHub RAG system implementing both Vector RAG and Graph RAG approaches.

## Setup

### Prerequisites

- Python 3.11+
- Poetry

### Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Development Commands

### Testing

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_hello.py

# Run tests in watch mode
poetry run pytest-watch
```

### Code Quality

```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Lint
poetry run ruff check src tests

# Type check
poetry run mypy src tests

# Run all checks
poetry run black src tests && \
poetry run isort src tests && \
poetry run ruff check src tests && \
poetry run mypy src tests
```

### Running the Application

```bash
# Run hello world example
poetry run python src/hello.py
```

## Project Structure

```
packages/server/
├── src/               # Source code
│   ├── __init__.py
│   └── hello.py       # Hello world example
├── tests/             # Test files
│   ├── __init__.py
│   └── test_hello.py  # Hello world tests
├── pyproject.toml     # Poetry dependencies and tool configs
└── poetry.toml        # Poetry settings (venv in project)
```

## Configuration

All tool configurations are in `pyproject.toml`:

- **Black**: Line length 100, Python 3.11 target
- **isort**: Black-compatible profile
- **Ruff**: Pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade
- **mypy**: Strict type checking enabled
- **pytest**: Coverage reporting, strict markers

## CI/CD

GitHub Actions workflow runs on every push/PR:
- Format checking (Black, isort)
- Linting (Ruff)
- Type checking (mypy)
- Tests with coverage

See `.github/workflows/server-ci.yml` for details.
