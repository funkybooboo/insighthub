import sys
from pathlib import Path

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from testcontainers.postgres import PostgresContainer
    from testcontainers.qdrant import QdrantContainer
    from testcontainers.rabbitmq import RabbitMqContainer

    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


@pytest.fixture(scope="function")
def postgres_container():
    """PostgreSQL test container."""
    if not TESTCONTAINERS_AVAILABLE:
        pytest.skip("testcontainers not available; skipping integration tests")
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="function")
def rabbitmq_container():
    """RabbitMQ test container."""
    if not TESTCONTAINERS_AVAILABLE:
        pytest.skip("testcontainers not available; skipping integration tests")
    with RabbitMqContainer("rabbitmq:3.12-alpine") as rabbitmq:
        yield rabbitmq


@pytest.fixture(scope="function")
def qdrant_container():
    """Qdrant test container."""
    if not TESTCONTAINERS_AVAILABLE:
        pytest.skip("testcontainers not available; skipping integration tests")
    with QdrantContainer("qdrant/qdrant:latest") as qdrant:
        yield qdrant
