import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.qdrant import QdrantContainer
from testcontainers.rabbitmq import RabbitMqContainer


@pytest.fixture(scope="function")
def postgres_container() -> PostgresContainer:
    """PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:15-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def rabbitmq_container() -> RabbitMqContainer:
    """RabbitMQ container for integration tests."""
    with RabbitMqContainer("rabbitmq:3.12-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def qdrant_container() -> QdrantContainer:
    """Qdrant container for integration tests."""
    with QdrantContainer("qdrant/qdrant:latest") as container:
        yield container
