# Quick Start Guide

Get up and running with InsightHub server in 5 minutes.

## Prerequisites

- Python 3.11+
- Poetry (package manager)
- Docker (for integration tests and production)

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
make test

# Run only unit tests (fast, no Docker needed)
make test-unit

# Run integration tests (requires Docker)
make test-integration
```

### What Happens During Integration Tests

When you run `make test-integration`:

1. **Docker containers start automatically**
   - PostgreSQL 16 container
   - MinIO (S3-compatible) container

2. **Tests run against real services**
   - Database operations use actual PostgreSQL
   - Blob storage uses actual MinIO
   - API tests use full application stack

3. **Containers stop automatically**
   - All containers are cleaned up
   - No manual cleanup needed

**No configuration required** - testcontainers handle everything!

## Development Workflow

### 1. Make Changes

Edit code in `src/` directory:
- `src/db/` - Database models and repositories
- `src/services/` - Business logic
- `src/routes/` - API endpoints
- `src/storage/` - Blob storage
- `src/rag/` - RAG library

### 2. Run Tests

```bash
# Fast feedback with unit tests
make test-unit

# Full validation with integration tests
make test-integration
```

### 3. Format and Lint

```bash
# Auto-format code
make format

# Check types
make type-check

# Run all checks
make check
```

### 4. Run Server Locally

```bash
# Start services with Docker Compose
docker compose up postgres minio

# Run Flask server
make server

# In another terminal, test it
curl http://localhost:5000/health
```

## Test Structure

```
tests/
├── unit/                    # Fast tests (< 1 sec)
│   ├── test_user_repository.py
│   ├── test_document_repository.py
│   └── test_document_service.py
│
└── integration/             # Slower tests (1-5 sec)
    ├── test_database_integration.py      # PostgreSQL
    ├── test_blob_storage.py              # MinIO
    └── test_api_endpoints.py             # Full API
```

## Common Commands

```bash
# Testing
make test                   # All tests with coverage
make test-unit              # Unit tests only
make test-integration       # Integration tests only

# Code Quality
make format                 # Format code
make lint                   # Run linter
make type-check             # Type check
make check                  # All quality checks

# Development
make install                # Install dependencies
make server                 # Run API server
make clean                  # Clean generated files
make help                   # Show all commands
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

**Solution**: Testcontainers automatically find free ports. If the issue persists:

```bash
# Stop conflicting services
docker compose down
```

### Tests Are Slow

**Issue**: Integration tests taking too long

**Solution**: Run unit tests for fast feedback

```bash
# Unit tests run in < 1 second
make test-unit

# Only run integration tests when needed
make test-integration
```

### Container Pull Failed

**Error**: `Failed to pull image postgres:16-alpine`

**Solution**: Check internet connection or use cached images

```bash
# Pre-pull images
docker pull postgres:16-alpine
docker pull minio/minio:latest
```

## Next Steps

- Read [TESTING.md](./testing.md) for detailed testing guide
- Read [DATABASE.md](./database.md) for database architecture
- Read [API.md](./api.md) for API documentation

## Key Features

- Auto-starting containers - No manual setup
- Fast unit tests - Instant feedback
- Real integration tests - Test against actual services
- Auto cleanup - Containers removed automatically
- Make commands - Simple, memorable commands
- Coverage reports - Track test coverage

## Example: Adding a New Feature

```bash
# 1. Write your code
vim src/services/new_feature.py

# 2. Write tests
vim tests/unit/test_new_feature.py

# 3. Run tests
make test-unit

# 4. Format code
make format

# 5. Run full validation
make check

# 6. Commit
git add .
git commit -m "Add new feature"
```

Done!
