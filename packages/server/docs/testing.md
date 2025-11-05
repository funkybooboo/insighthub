# Testing Guide

This document describes the testing strategy and how to run tests for the InsightHub server.

## Test Structure

Tests are organized into two categories:

```
tests/
  +-- unit/                 # Unit tests (fast, isolated)
  |   +-- test_user_repository.py
  |   +-- test_document_repository.py
  |   +-- test_document_service.py
  +-- integration/          # Integration tests (slower, use containers)
      +-- test_database_integration.py
      +-- test_blob_storage.py
      +-- test_api_endpoints.py
```

## Test Types

### Unit Tests

Unit tests are fast, isolated tests that test individual components without external dependencies.

- **Location**: `tests/unit/`
- **Run time**: < 1 second per test
- **Dependencies**: In-memory database sessions
- **What they test**:
  - Repository CRUD operations
  - Service business logic
  - Data validation
  - Model relationships

**Example**:
```python
def test_create_user(db_session: Session) -> None:
    """Test creating a new user."""
    repo = UserRepository(db_session)
    user = repo.create(username="testuser", email="test@example.com")
    assert user.id is not None
```

### Integration Tests

Integration tests verify that components work together correctly using real services in Docker containers.

- **Location**: `tests/integration/`
- **Run time**: 1-5 seconds per test
- **Dependencies**: Testcontainers (PostgreSQL, MinIO)
- **What they test**:
  - Database operations with real PostgreSQL
  - Blob storage operations with real MinIO
  - API endpoints with full stack
  - Cascade deletes and foreign keys
  - Transaction handling

**Example**:
```python
def test_upload_and_download_file(blob_storage: S3BlobStorage) -> None:
    """Test uploading and downloading from real MinIO."""
    file_obj = BytesIO(b"test content")
    blob_storage.upload_file(file_obj, "test/file.txt")
    downloaded = blob_storage.download_file("test/file.txt")
    assert downloaded == b"test content"
```

## Running Tests

### Prerequisites

1. **Docker**: Required for integration tests with testcontainers
2. **Poetry**: Package manager

```bash
# Install dependencies
poetry install

# Ensure Docker is running (for integration tests)
docker ps
```

### Run All Tests

```bash
# Using Make (recommended)
make test

# Using pytest directly
poetry run pytest

# Run with verbose output
poetry run pytest -v
```

### Run Specific Test Categories

```bash
# Using Make
make test-unit          # Run only unit tests (fast, no Docker needed)
make test-integration   # Run only integration tests (requires Docker)

# Using pytest directly
poetry run pytest tests/unit/ -v           # Unit tests only
poetry run pytest tests/integration/ -v    # Integration tests only

# Run specific test file
poetry run pytest tests/unit/test_user_repository.py -v

# Run specific test function
poetry run pytest tests/unit/test_user_repository.py::test_create_user -v
```

### Testcontainers Auto-Start

Integration tests automatically start required Docker containers:

```bash
# This command will:
# 1. Start PostgreSQL container (first time only in session)
# 2. Start MinIO container (first time only in session)
# 3. Run all integration tests
# 4. Stop and remove containers automatically
make test-integration
```

**Output you'll see:**
```
[TESTCONTAINERS] Starting PostgreSQL container...
[TESTCONTAINERS] PostgreSQL started: postgresql://test:test@localhost:32768/test
[TESTCONTAINERS] Starting MinIO container...
[TESTCONTAINERS] MinIO started: http://localhost:32769
... tests run ...
[TESTCONTAINERS] Stopping PostgreSQL container...
[TESTCONTAINERS] Stopping MinIO container...
```

**Important**: Docker must be running before executing integration tests!

### Run Tests with Markers

```bash
# Run only database tests
poetry run pytest -m database

# Run only API tests
poetry run pytest -m api

# Skip slow tests
poetry run pytest -m "not slow"
```

## Test Fixtures

### Database Fixtures

Provided by `conftest.py`:

- **`postgres_container`**: PostgreSQL testcontainer (session scope)
- **`db_engine`**: SQLAlchemy engine (function scope)
- **`db_session`**: Database session (function scope)
- **`test_database_url`**: Connection URL string

**Usage**:
```python
def test_example(db_session: Session) -> None:
    # db_session is automatically created and torn down
    user_repo = UserRepository(db_session)
    user = user_repo.create(username="test", email="test@example.com")
```

### Blob Storage Fixtures

- **`minio_container`**: MinIO testcontainer (session scope)
- **`blob_storage`**: S3BlobStorage instance (function scope)

**Usage**:
```python
def test_example(blob_storage: S3BlobStorage) -> None:
    # Blob storage connected to temporary MinIO container
    blob_storage.upload_file(file_obj, "test.txt")
```

### Sample Data Fixtures

- **`sample_text_file`**: BytesIO with text content
- **`sample_pdf_file`**: BytesIO with minimal valid PDF

**Usage**:
```python
def test_example(sample_text_file: BytesIO) -> None:
    # Use pre-created sample file
    text = extract_text(sample_text_file, "test.txt")
```

## Testcontainers

Integration tests use [testcontainers-python](https://testcontainers-python.readthedocs.io/) to spin up real services:

### PostgreSQL Container

```python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres
```

- Automatically starts PostgreSQL 16
- Creates temporary database
- Tears down after test session
- Each test function gets a clean schema

### MinIO Container

```python
@pytest.fixture(scope="session")
def minio_container():
    with MinioContainer() as minio:
        yield minio
```

- Automatically starts MinIO
- Creates temporary bucket
- Tears down after test session
- S3-compatible object storage

## Code Coverage

Generate coverage reports:

```bash
# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Coverage Goals**:
- Overall: > 80%
- Critical paths (repositories, services): > 90%
- API endpoints: > 85%

## Testing Best Practices

### 1. Test Naming

Use descriptive test names that explain what is being tested:

```python
# Good
def test_create_user_with_valid_data() -> None:
    ...

def test_upload_document_rejects_invalid_file_type() -> None:
    ...

# Bad
def test_user() -> None:
    ...

def test_upload() -> None:
    ...
```

### 2. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
def test_delete_user() -> None:
    # Arrange
    repo = UserRepository(db_session)
    user = repo.create(username="test", email="test@example.com")

    # Act
    result = repo.delete(user.id)

    # Assert
    assert result is True
    assert repo.get_by_id(user.id) is None
```

### 3. Test One Thing

Each test should verify one specific behavior:

```python
# Good - tests one thing
def test_create_user_sets_timestamps() -> None:
    user = repo.create(username="test", email="test@example.com")
    assert user.created_at is not None
    assert user.updated_at is not None

# Bad - tests multiple things
def test_user_operations() -> None:
    user = repo.create(...)  # create
    user = repo.update(...)  # update
    repo.delete(...)         # delete
```

### 4. Use Fixtures for Common Setup

Extract common setup to fixtures:

```python
@pytest.fixture
def test_user(db_session: Session) -> User:
    user_repo = UserRepository(db_session)
    return user_repo.create(username="testuser", email="test@example.com")

def test_create_document(db_session: Session, test_user: User) -> None:
    # test_user is already created
    doc_repo = DocumentRepository(db_session)
    doc = doc_repo.create(user_id=test_user.id, ...)
```

### 5. Clean Up Resources

Fixtures automatically clean up:

```python
@pytest.fixture
def db_session(db_engine):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # Clean up
        session.close()
```

## Continuous Integration

Tests run automatically on:
- Every push to repository
- Pull requests
- Pre-commit hooks (optional)

**GitHub Actions** (when configured):
```yaml
- name: Run tests
  run: |
    poetry install
    poetry run pytest --cov=src --cov-report=xml
```

## Debugging Tests

### Run with Print Statements

```bash
# Print statements will show
poetry run pytest -s tests/unit/test_user_repository.py
```

### Run with PDB Debugger

```python
def test_example() -> None:
    import pdb; pdb.set_trace()
    # Test code
```

```bash
poetry run pytest --pdb
```

### View Container Logs

```python
def test_example(postgres_container):
    # Print container logs
    print(postgres_container.get_logs())
```

## Common Issues

### 1. Docker Not Running

**Error**: `Cannot connect to Docker daemon`

**Solution**: Start Docker Desktop or Docker daemon

### 2. Port Already in Use

**Error**: `Port 5432 is already allocated`

**Solution**: Testcontainers automatically find free ports. If issue persists, stop conflicting services.

### 3. Slow Tests

**Issue**: Integration tests take too long

**Solution**:
- Run unit tests only: `pytest tests/unit/`
- Use session-scoped containers (already configured)
- Parallelize with pytest-xdist: `pytest -n auto`

### 4. Connection Refused

**Error**: `Connection refused to testcontainer`

**Solution**: Testcontainers wait for health checks. If persists, check Docker networking.

## Writing New Tests

### 1. Unit Test Template

```python
"""Unit tests for NewFeature."""

import pytest
from sqlalchemy.orm import Session

def test_new_feature(db_session: Session) -> None:
    """Test description."""
    # Arrange
    # ... setup

    # Act
    # ... execute

    # Assert
    assert result == expected
```

### 2. Integration Test Template

```python
"""Integration tests for NewFeature."""

import pytest

def test_new_feature_integration(
    db_session: Session,
    blob_storage: S3BlobStorage
) -> None:
    """Test description with real services."""
    # Arrange
    # ... setup

    # Act
    # ... execute

    # Assert
    assert result == expected
```

## Test Coverage Report

After running tests, view coverage:

```bash
# Terminal summary
poetry run pytest --cov=src --cov-report=term-missing

# HTML report
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

The report shows:
- Which lines are covered
- Which lines are missing coverage
- Branch coverage
- Overall percentage
