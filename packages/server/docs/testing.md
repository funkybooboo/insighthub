# Testing Guide

This document explains the testing philosophy and practices for the InsightHub server.

## Testing Philosophy

We follow a strict separation between unit tests and integration tests:

### Unit Tests
- **Fast** (< 100ms per test)
- **No external dependencies** (no Docker, no network calls)
- **Use dummy implementations** (InMemoryBlobStorage, SQLite in-memory)
- **Test one component in isolation**
- Located in `tests/unit/`

### Integration Tests
- **Test real component interactions**
- **Use testcontainers** (temporary Docker containers)
- **Use real implementations** (PostgreSQL, MinIO/S3)
- **Slower execution** (1-5s per test)
- Located in `tests/integration/`

## Running Tests

### Run All Tests
```bash
poetry run pytest
```

### Run Only Unit Tests
```bash
poetry run pytest tests/unit/ -v
```

### Run Only Integration Tests
```bash
poetry run pytest tests/integration/ -v
```

### Run Tests by Marker
```bash
# Run only fast unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Skip slow tests
poetry run pytest -m "not slow"
```

### Run Tests with Coverage
```bash
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Test Structure

### Unit Test Example

Unit tests use dummy implementations (in-memory database, in-memory blob storage):

```python
# tests/unit/test_user_service.py
import pytest
from tests.unit.conftest import *  # Gets unit test fixtures

def test_create_user(test_context):
    """Test creating a user with in-memory implementations."""
    # test_context uses SQLite in-memory + InMemoryBlobStorage
    user = test_context.user_service.create_user(
        username="test_user",
        email="test@example.com"
    )

    assert user.username == "test_user"
    # Fast: no external dependencies!
```

### Integration Test Example

Integration tests use real implementations with testcontainers:

```python
# tests/integration/test_user_service_integration.py
import pytest
from tests.conftest import *  # Gets integration test fixtures

@pytest.mark.integration
def test_create_user_with_real_database(test_context):
    """Test creating a user with real PostgreSQL."""
    # test_context uses PostgreSQL testcontainer + MinIO testcontainer
    user = test_context.user_service.create_user(
        username="test_user",
        email="test@example.com"
    )

    # Verify data is actually in PostgreSQL
    assert user.id is not None
    # Real database interaction!
```

## Conditional Test Execution

Some tests require external services. Use skip helpers to gracefully skip tests when services aren't available:

### Skip if OpenAI Not Configured

```python
from tests.conftest import skip_if_no_openai

@skip_if_no_openai()
@pytest.mark.requires_openai
def test_openai_embeddings():
    """Test OpenAI embeddings (only runs if API key configured)."""
    # This test only runs if OPENAI_API_KEY is set in .env
    pass
```

### Skip if Ollama Not Running

```python
from tests.conftest import skip_if_no_ollama

@skip_if_no_ollama()
@pytest.mark.requires_ollama
def test_ollama_embeddings():
    """Test Ollama embeddings (only runs if Ollama is running)."""
    # This test only runs if Ollama is accessible at OLLAMA_BASE_URL
    pass
```

### Skip if Qdrant Not Running

```python
from tests.conftest import skip_if_no_qdrant

@skip_if_no_qdrant()
@pytest.mark.requires_qdrant
def test_qdrant_vector_store():
    """Test Qdrant vector store (only runs if Qdrant is running)."""
    # This test only runs if Qdrant is accessible
    pass
```

## Available Pytest Markers

```python
@pytest.mark.unit           # Fast unit test, no external dependencies
@pytest.mark.integration    # Integration test with testcontainers
@pytest.mark.database       # Test requires database
@pytest.mark.blob_storage   # Test requires blob storage
@pytest.mark.api            # API endpoint test
@pytest.mark.slow           # Test takes > 1 second
@pytest.mark.requires_openai   # Test requires OpenAI API key
@pytest.mark.requires_ollama   # Test requires Ollama running
@pytest.mark.requires_qdrant   # Test requires Qdrant running
@pytest.mark.requires_s3       # Test requires S3/MinIO credentials
```

## Test Fixtures

### Unit Test Fixtures (tests/unit/conftest.py)

```python
# SQLite in-memory database
unit_db_engine  # In-memory database engine
db_session      # Database session (SQLite)

# Test context with dummy implementations
test_context    # UnitTestContext with InMemoryBlobStorage

# Repositories (SQL implementations with SQLite)
user_repository
document_repository
chat_session_repository
chat_message_repository

# Blob storage (dummy implementation)
blob_storage    # InMemoryBlobStorage

# Sample data
sample_text_file
sample_pdf_file
```

### Integration Test Fixtures (tests/conftest.py)

```python
# Testcontainers
postgres_container  # PostgreSQL testcontainer
minio_container     # MinIO testcontainer

# Real database
db_engine       # PostgreSQL engine from testcontainer
db_session      # PostgreSQL session

# Test context with real implementations
test_context    # IntegrationTestContext with real PostgreSQL + MinIO

# Repositories (SQL implementations with PostgreSQL)
user_repository
document_repository
chat_session_repository
chat_message_repository

# Blob storage (real implementation)
blob_storage    # MinioBlobStorage from testcontainer

# Sample data
sample_text_file
sample_pdf_file
```

## Writing New Tests

### Unit Test Template

```python
# tests/unit/test_my_component.py
"""Unit tests for MyComponent."""

import pytest


class TestMyComponent:
    """Unit tests for MyComponent."""

    def test_basic_operation(self):
        """Test basic operation with no dependencies."""
        # Use dummy implementations, no external services
        result = my_function()
        assert result == expected_value

    def test_with_blob_storage(self, blob_storage):
        """Test with in-memory blob storage."""
        # blob_storage is InMemoryBlobStorage
        blob_storage.upload_file(file_obj, "test.txt")
        content = blob_storage.download_file("test.txt")
        assert content == expected_content
```

### Integration Test Template

```python
# tests/integration/test_my_component_integration.py
"""Integration tests for MyComponent."""

import pytest


@pytest.mark.integration
class TestMyComponentIntegration:
    """Integration tests for MyComponent."""

    def test_with_real_database(self, db_session):
        """Test with real PostgreSQL database."""
        # db_session is connected to PostgreSQL testcontainer
        result = my_database_operation(db_session)
        assert result is not None

    def test_with_real_blob_storage(self, blob_storage):
        """Test with real MinIO blob storage."""
        # blob_storage is connected to MinIO testcontainer
        blob_storage.upload_file(file_obj, "test.txt")
        # Verify file actually uploaded to MinIO
        assert blob_storage.file_exists("test.txt")
```

## Test Configuration

Tests automatically load `.env.test` (see `src/config.py`):

```python
# config.py
if os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv(".env.test", override=True)
```

**`.env.test` Configuration**:
- Uses `in_memory` blob storage for unit tests
- Uses `sqlite:///:memory:` for unit test database
- Integration tests override with testcontainers
- Smaller chunk sizes for faster tests
- Lower limits for faster tests

## Best Practices

### DO ✓

- **Unit Tests**: Use dummy implementations (InMemoryBlobStorage, SQLite)
- **Integration Tests**: Use testcontainers (PostgreSQL, MinIO)
- **Mark tests properly**: Use `@pytest.mark.unit` or `@pytest.mark.integration`
- **Skip unavailable services**: Use skip helpers for optional dependencies
- **Test one thing**: Each test should have a single, clear purpose
- **Clean up**: Fixtures handle cleanup automatically
- **Fast unit tests**: Keep unit tests under 100ms

### DON'T ✗

- **Don't use mocks** in unit tests - use real dummy implementations instead
- **Don't test implementation details** - test behavior and interfaces
- **Don't require external services** for unit tests
- **Don't commit test data** to the repository
- **Don't share state** between tests - each test should be independent
- **Don't use real APIs** without skip helpers

## Troubleshooting

### Tests are slow
- Run only unit tests: `pytest tests/unit/`
- Skip integration tests: `pytest -m "not integration"`
- Use pytest-xdist for parallel execution: `pytest -n auto`

### Testcontainer fails to start
- Ensure Docker is running: `docker info`
- Check Docker socket permissions
- Try pulling images manually: `docker pull postgres:16-alpine`

### Tests fail with "Service unavailable"
- Check if service is required for test
- Use appropriate skip helper
- Verify service is running (for integration tests)

### Import errors
- Ensure virtual environment is activated: `poetry shell`
- Install dependencies: `poetry install`
- Check PYTHONPATH includes project root

## Coverage Goals

- **Overall**: > 80% coverage
- **Critical paths**: 100% coverage (factories, repositories, services)
- **Integration points**: Covered by integration tests
- **Edge cases**: Covered by unit tests

Run coverage report:
```bash
poetry run pytest --cov=src --cov-report=term-missing
```

## CI/CD Integration

Tests run automatically in GitHub Actions:
- Unit tests run on every push
- Integration tests run on every push
- Coverage reports uploaded to coverage service
- Failed tests block PR merges

See `.github/workflows/server-ci.yml` for details.
