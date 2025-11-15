# InsightHub Server

Python backend for the InsightHub RAG system, providing a complete API for document management, chat with RAG, and real-time streaming responses.

## Features

- **Vector RAG Implementation**: Document ingestion, chunking, embedding, and retrieval
- **Real-time Streaming**: WebSocket-based token streaming for chat responses
- **Document Management**: Upload, store, and query PDF/text documents
- **Chat Sessions**: Persistent conversation memory with context
- **Multiple LLM Providers**: Ollama, OpenAI, Claude, HuggingFace support
- **Modular Architecture**: Pluggable components (embeddings, chunking, vector stores)
- **REST API**: Full CRUD operations for documents and chat
- **CLI Interface**: Command-line tools for document management and chat
- **Database Integration**: PostgreSQL with SQLAlchemy ORM

## Tech Stack

- **Python 3.11+** with FastAPI/Flask
- **SQLAlchemy** for database ORM
- **Socket.IO** for real-time communication
- **Poetry** for dependency management
- **Pytest** for testing
- **Docker** for containerization

## Setup

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL (or Docker for local development)

### Installation

```bash
cd packages/server

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

### Running the Application

```bash
# Start the API server
poetry run python -m src.api

# Start with CLI interface
poetry run python -m src.cli --help

# Available CLI commands:
poetry run python -m src.cli upload <file>     # Upload a document
poetry run python -m src.cli list              # List all documents
poetry run python -m src.cli delete <doc_id>   # Delete a document
poetry run python -m src.cli chat <message>    # Send a chat message
poetry run python -m src.cli sessions          # List chat sessions
poetry run python -m src.cli interactive       # Start interactive chat
```

### Testing

See [TESTING.md](../../TESTING.md) for the complete testing guide.

```bash
# Unit Tests (Pytest)
task test                  # All tests with coverage
task test-unit             # Unit tests only (fast)
task test-integration      # Integration tests (requires Docker)
task test-watch            # Watch mode

# API Tests (Bruno)
task test:api              # Run Bruno API tests (requires Bruno CLI)
task test:api:verbose      # With verbose output

# Using Poetry directly
poetry run pytest                           # Run all tests
poetry run pytest --cov=src --cov-report=html  # With coverage
poetry run pytest tests/unit/               # Unit tests only
poetry run pytest tests/integration/        # Integration tests only
```

**Prerequisites for API Tests**:
```bash
# Install Bruno CLI globally
npm install -g @usebruno/cli

# Make sure server is running
task server  # In one terminal
task test:api  # In another terminal
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
task check  # From packages/server/ directory
```

## Project Structure

```
packages/server/
├── src/                    # Source code
│   ├── domains/           # Business logic domains
│   │   ├── auth/          # User authentication
│   │   ├── chat/          # Chat and conversation management
│   │   ├── documents/     # Document upload and management
│   │   ├── health/        # Health check endpoints
│   │   └── users/         # User management
│   ├── infrastructure/    # Infrastructure services
│   │   ├── auth/          # JWT authentication
│   │   ├── database/      # Database connection and session management
│   │   ├── errors/        # Error handling and DTOs
│   │   ├── factories/     # Service factories
│   │   ├── llm/           # LLM provider implementations
│   │   ├── middleware/    # Flask middleware (logging, security, etc.)
│   │   ├── rag/           # RAG implementations and components
│   │   │   ├── chunking/  # Text chunking strategies
│   │   │   ├── embeddings/# Embedding model providers
│   │   │   └── vector_stores/  # Vector database implementations
│   │   ├── socket/        # WebSocket/Socket.IO handlers
│   │   └── storage/       # File/blob storage backends
│   ├── api.py             # Flask application factory
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Application configuration
│   └── context.py         # Application context with services
├── tests/                 # Test files
│   ├── unit/              # Unit tests with dummy implementations
│   ├── integration/       # Integration tests with real services
│   └── conftest.py        # Test configuration
├── pyproject.toml         # Poetry dependencies and tool configs
├── poetry.toml            # Poetry settings (venv in project)
└── README.md              # This file
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
