# Quick Start Guide

Get up and running with InsightHub Flask server in 5 minutes.

## Prerequisites

- Python 3.11+
- Poetry (package manager)
- Docker (for integration tests and production)
- Node.js 18+ (for frontend development)

## Installation

```bash
cd packages/server

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
task test

# Run only unit tests (fast, no Docker needed)
task test-unit

# Run integration tests (requires Docker)
task test-integration
```

### What Happens During Integration Tests

When you run `task test-integration`:

1. **Docker containers start automatically**
   - PostgreSQL container
   - Redis container
   - Qdrant container
   - Neo4j container (if available)

2. **Tests run against real services**
   - Database operations use actual PostgreSQL
   - Cache operations use actual Redis
   - Vector operations use actual Qdrant
   - API tests use full application stack

3. **Containers stop automatically**
   - All containers are cleaned up
   - No manual cleanup needed

**No configuration required** - testcontainers handle everything!

## Development Workflow

### 1. Make Changes

Edit code in `src/` directory:
- `src/domains/` - Business logic by feature (auth, chat, documents, users, health)
- `src/infrastructure/` - External integrations (database, rag, llm, storage)
- `src/api.py` - Flask application entry point
- `src/context.py` - Application context and configuration

### 2. Run Tests

```bash
# Fast feedback with unit tests
task test-unit

# Full validation with integration tests
task test-integration
```

### 3. Format and Lint

```bash
# Auto-format code
task format

# Check types
task type-check

# Run all checks
task check
```

### 4. Run Server Locally

```bash
# Start infrastructure services with Docker Compose
task up-infra

# Run Flask server
task server

# In another terminal, test it
curl http://localhost:5000/health
```

## Test Structure

```
tests/
- unit/                    # Fast tests (< 1 sec)
|   - test_user_repository.py
|   - test_document_repository.py
|   - test_chat_service.py
|   - test_rag_service.py
|
- integration/             # Slower tests (1-5 sec)
    - test_database_integration.py      # PostgreSQL
    - test_qdrant_integration.py        # Vector database
    - test_neo4j_integration.py        # Graph database
    - test_api_endpoints.py             # Full API
    - test_worker_integration.py        # Worker communication
```

## Common Commands

```bash
# Testing
task test                   # All tests with coverage
task test-unit              # Unit tests only
task test-integration       # Integration tests only

# Code Quality
task format                 # Format code
task lint                   # Run linter
task type-check             # Type check
task check                  # All quality checks

# Development
task install                # Install dependencies
task server                 # Run API server
task clean                  # Clean generated files
task --list                 # Show all commands
```

## Viewing Test Coverage

After running tests:

```bash
# View in browser
open htmlcov/index.html

# Or view in terminal
poetry run pytest --cov=src --cov-report=term-missing
```

## Troubleshooting

### Docker Not Running

**Error**: `Cannot connect to Docker daemon`

**Solution**: Start Docker Desktop or Docker daemon

```bash
# Check if Docker is running
docker ps
```

### Port Already in Use

**Error**: `Port 5432 is already allocated`

**Solution**: Testcontainers automatically find free ports. If issue persists:

```bash
# Stop conflicting services
docker compose down
```

### Tests Are Slow

**Issue**: Integration tests taking too long

**Solution**: Run unit tests for fast feedback

```bash
# Unit tests run in < 1 second
task test-unit

# Only run integration tests when needed
task test-integration
```

### Container Pull Failed

**Error**: `Failed to pull image postgres:16-alpine`

**Solution**: Check internet connection or use cached images

```bash
# Pre-pull images
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull qdrant/qdrant:latest
```

## Flask Development Server

The Flask server runs on `http://localhost:5000` by default with:

- **REST API**: All endpoints under `/api/`
- **WebSocket**: Socket.IO integration for real-time chat
- **Health Checks**: `/health` endpoint for monitoring
- **CORS**: Configured for frontend development

## Environment Configuration

Key environment variables for development:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/insighthub

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## Next Steps

- Read [TESTING.md](./testing.md) for detailed testing guide
- Read [DATABASE.md](./database.md) for database architecture
- Read [API.md](./api.md) for API documentation
- Read [MIDDLEWARE.md](./middleware.md) for middleware configuration

## Key Features

- **Auto-starting containers** - No manual setup required
- **Fast unit tests** - Instant feedback loop
- **Real integration tests** - Test against actual services
- **Auto cleanup** - Containers removed automatically
- **Task commands** - Simple, memorable commands
- **Coverage reports** - Track test coverage effectively
- **Flask integration** - Full Flask application stack
- **Clean architecture** - Domains and infrastructure separation

## Example: Adding a New Feature

```bash
# 1. Write your code
vim src/domains/new_feature.py

# 2. Write tests
vim tests/unit/test_new_feature.py

# 3. Run tests
task test-unit

# 4. Format code
task format

# 5. Run full validation
task check

# 6. Commit
git add .
git commit -m "feat: add new feature"
```

Done!