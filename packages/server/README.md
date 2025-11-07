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

# Set up environment variables
cp .env.example .env
# Edit .env with your local configuration

# Optional: For completely local setup (no cloud services)
cp .env.local.example .env.local
# Edit .env.local - this overrides .env

# For running tests, create .env.test
cp .env.example .env.test
# Edit .env.test with test-specific configuration
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
+-- src/               # Source code
|   +-- __init__.py
|   +-- hello.py       # Hello world example
+-- tests/             # Test files
|   +-- __init__.py
|   +-- test_hello.py  # Hello world tests
+-- pyproject.toml     # Poetry dependencies and tool configs
+-- poetry.toml        # Poetry settings (venv in project)
```

## Configuration

### Environment Variables

The application uses environment variables for configuration:

- **`.env.example`** - Template file showing all available configuration options (committed to git)
- **`.env.local.example`** - Template for local-only setup with no cloud services (committed to git)
- **`.env`** - Your local development configuration (gitignored, create from `.env.example`)
- **`.env.local`** - Local-only overrides (gitignored, optional, create from `.env.local.example`)
- **`.env.test`** - Test environment configuration (gitignored, create from `.env.example`)

**Setup**:
1. Copy `.env.example` to `.env`
2. Update values in `.env` for your local environment
3. (Optional) For local-only setup: Copy `.env.local.example` to `.env.local`
4. For tests, copy `.env.example` to `.env.test` and customize test settings

**Config Priority**: `.env.local` > `.env` > environment variables

**Key Configuration Sections**:
- **Service Types**: Choose implementations for services (default, etc.)
- **Repository Types**: Choose implementations for repositories (sql, etc.)
- **Blob Storage**: Choose storage backend (s3, file_system, in_memory)
- **Database**: PostgreSQL connection string
- **RAG Settings**: Chunking strategy, embedding model, vector store

**Production**: Use environment variables directly (Docker, Kubernetes, etc.) instead of `.env` files.

### Tool Configuration

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
