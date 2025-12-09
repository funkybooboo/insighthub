# Testing Strategy for InsightHub

This document outlines the testing philosophy and requirements for the InsightHub project. All tests must follow these strict principles to ensure maintainability, reliability, and confidence in the codebase.

## STRICT TESTING PRINCIPLES

**Only write tests that add value**. Every test must:
- Test **input/output behavior**, not implementation details
- Test **public APIs and contracts**, never private methods or internal state
- Provide **confidence in correctness** without being brittle
- **Never test implementation** - tests should survive refactoring

## Unit Tests (`tests/unit/`)

**MANDATORY**: Use **dummy implementations**, NEVER mocks.

### Why Dummies Over Mocks?
- Dummies are **real implementations** that can be reused across tests
- More closely resemble **production code paths**
- **Easier to maintain** than complex mock expectations
- **Catch interface changes** at compile time
- **Test actual behavior**, not mocked behavior

### Unit Test Guidelines:
- Test **one component in isolation**
- Use **dummy implementations** for dependencies (never mocks)
- **No external services** (no Docker, no network calls)
- **Fast execution** (< 100ms per test)
- **Test public APIs only** - never test private methods
- **Test input/output contracts** - verify what the function does, not how

### Example Unit Test:
```python
def test_vector_rag_add_documents():
    # Arrange: Use real implementations with dummies
    dummy_store = InMemoryVectorStore()
    dummy_embeddings = DummyEmbeddings()
    dummy_chunker = CharacterChunker(chunk_size=10)

    rag = VectorRag(
        vector_store=dummy_store,
        embedding_model=dummy_embeddings,
        chunker=dummy_chunker
    )

    # Act: Test the public API
    count = rag.add_documents([{"text": "test document"}])

    # Assert: Verify output, not internal state
    assert count > 0  # Tests the contract: document were added
```

## Integration Tests (`tests/integration/`)

**MANDATORY**: Use **testcontainers** for all external dependencies.

### Why Test Containers?
- Tests run against **real databases and services** (Qdrant, Neo4j, Redis)
- Catch **integration bugs** that unit tests miss
- **Clean slate** for each test run - no shared state
- **No shared state** between test runs
- **Isolated environments** prevent test interference

### Integration Test Guidelines:
- Test **component interactions** with real dependencies
- Use **testcontainers** for databases (Qdrant, Neo4j, PostgreSQL)
- **MANDATORY**: Containers are created/destroyed per test function
- **Slower execution** (1-5s per test) is acceptable
- **Never use mocks** in integration tests

### Example Integration Test:
```python
import pytest
from testcontainers.qdrant import QdrantContainer

@pytest.fixture(scope="function")
def qdrant_container():
    """MANDATORY: Spin up temporary Qdrant container for test."""
    with QdrantContainer("qdrant/qdrant:latest") as container:
        yield container

def test_qdrant_vector_store_integration(qdrant_container):
    # Use real Qdrant running in Docker - no mocks allowed
    store = QdrantVectorStore(
        host=qdrant_container.get_container_host_ip(),
        port=qdrant_container.get_exposed_port(6333),
        collection_name="test_collection"
    )

    # Test actual database operations
    store.add(vectors=[[0.1, 0.2]], ids=["1"], metadata=[{"test": "data"}])
    results = store.search(query_vector=[0.1, 0.2], top_k=1)
    assert len(results) == 1
```

## 3rd Party API Tests

**MANDATORY**: For 3rd party APIs, write two sets of tests to avoid code duplication and expensive API calls.

### Strategy:
- **Faker Tests** (default): Use faker library to mock 3rd party API responses
- **Real API Tests** (optional): Use actual 3rd party APIs, skipped unless explicitly enabled
- **No Code Duplication**: Use parameterized tests or shared fixtures to avoid duplicating test logic

### Guidelines:
- **Default Behavior**: Tests use faker implementations by default (fast, reliable, no API costs)
- **Real API Testing**: Real API tests are skipped unless `TEST_REAL_APIS=true` environment variable is set
- **Cost Management**: Never run real API tests in CI/CD unless explicitly configured
- **Rate Limiting**: Real API tests should respect rate limits and include delays between calls
- **Error Handling**: Test both success and failure scenarios for both faker and real implementations

### Example Implementation:
```python
import pytest
import os
from faker import Faker

# Shared test logic - no duplication
def _test_api_integration(api_client, expected_response_structure):
    """Shared test logic that works with both faker and real implementations."""
    response = api_client.make_request()
    assert response.status_code == 200
    assert expected_response_structure in response.data

@pytest.fixture
def faker_api_client():
    """Faker implementation for fast, reliable testing."""
    fake = Faker()
    return FakerAPIClient(fake)

@pytest.fixture
def real_api_client():
    """Real API implementation - expensive, rate-limited."""
    return RealAPIClient(api_key=os.getenv("API_KEY"))

@pytest.mark.skipif(
    os.getenv("TEST_REAL_APIS") != "true",
    reason="Real API tests are expensive and skipped by default"
)
def test_real_api_integration(real_api_client):
    """Test against real 3rd party API - only runs when TEST_REAL_APIS=true."""
    _test_api_integration(real_api_client, "real_data_field")

def test_faker_api_integration(faker_api_client):
    """Test against faker implementation - runs by default."""
    _test_api_integration(faker_api_client, "fake_data_field")
```

### Running 3rd Party API Tests:

```bash
# Run faker tests only (default, fast)
poetry run pytest tests/ -k "api" -v

# Run real API tests (expensive, requires API keys)
TEST_REAL_APIS=true poetry run pytest tests/ -k "real_api" -v

# Run all API tests (faker + real if enabled)
TEST_REAL_APIS=true poetry run pytest tests/ -k "api" -v
```

## Test Organization

```
tests/
+-- unit/                    # Unit tests with dummies
\-- integration/             # Integration tests with containers
```

## Running Tests

```bash
# Run all tests
poetry run pytest tests/ -v --cov=src

# Run unit tests only
poetry run pytest tests/unit/ -v

# Run integration tests only
poetry run pytest tests/integration/ -v

# Run with coverage
poetry run pytest tests/ --cov=src --cov-report=html
```

## Key Requirements

1. **No Mocks**: Use dummy implementations instead of mocks in unit tests
2. **Testcontainers**: Use testcontainers for all external dependencies in integration tests
3. **3rd Party APIs**: Use faker implementations by default, real APIs only when explicitly enabled
4. **Public APIs Only**: Never test private methods or implementation details
5. **Behavior Over Implementation**: Test what functions do, not how they do it
6. **Fast Unit Tests**: Unit tests must execute in < 100ms
7. **Isolated Integration Tests**: Each integration test gets a clean container environment
8. **No Code Duplication**: Use shared test logic for faker vs real API implementations

## Quality Gates

All tests must pass in CI/CD pipelines. Tests that are slow, brittle, or test implementation details will be rejected during code review.</content>
<parameter name="filePath">tests/README.md