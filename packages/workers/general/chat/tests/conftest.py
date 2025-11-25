"""Test configuration and fixtures for chat worker tests."""

import os
import sys
from unittest.mock import Mock

import pytest

# Set environment variable to indicate we're in testing mode
os.environ["CHAT_WORKER_TESTING"] = "1"

# Check if we're running integration tests

is_integration_test = any("integration" in arg for arg in sys.argv)


# Mock shared modules before any imports
class MockConfig:
    rabbitmq_url = "amqp://localhost:5672/"
    rabbitmq_exchange = "chat_exchange"
    database_url = "postgresql://user:pass@localhost:5432/test"
    ollama_base_url = "http://localhost:11434"
    ollama_llm_model = "llama3.2"
    ollama_embedding_model = "nomic-embed-text"
    qdrant_host = "localhost"
    qdrant_port = 6333
    worker_concurrency = 1


class MockCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, query, params=None):
        pass

    def fetchall(self):
        return []

    def fetchone(self):
        return {
            "rag_collection": "test_collection",
            "top_k": 8,
            "embedding_dim": 768,
            "embedding_model": "nomic-embed-text",
        }


class MockPostgresConnection:
    def __init__(self, db_url=None):
        pass

    def connect(self):
        pass

    def get_cursor(self, as_dict=False):
        return MockCursor()


class MockLogger:
    def info(self, message, extra=None):
        pass

    def error(self, message, extra=None):
        pass

    def warning(self, message, extra=None):
        pass

    def debug(self, message, extra=None):
        pass


def mock_get_logger(name):
    return MockLogger()


class MockWorker:
    def __init__(self, **kwargs):
        pass

    def publish_event(self, event_name, data):
        pass


# For integration tests, don't mock shared modules since we want to test with real dependencies
# For unit tests, mock them
if not is_integration_test:
    # Mock shared modules for unit tests
    sys.modules["shared"] = Mock()
    sys.modules["shared.config"] = Mock()
    sys.modules["shared.config"].config = MockConfig()
    sys.modules["shared.database"] = Mock()
    sys.modules["shared.database.sql"] = Mock()
    sys.modules["shared.database.sql.postgres"] = Mock()
    sys.modules["shared.database.sql.postgres"].PostgresConnection = MockPostgresConnection
    sys.modules["shared.database.vector"] = Mock()
    sys.modules["shared.documents"] = Mock()
    sys.modules["shared.documents.embedding"] = Mock()
    sys.modules["shared.orchestrators"] = Mock()
    sys.modules["shared.llm"] = Mock()
    sys.modules["shared.logger"] = Mock()
    sys.modules["shared.logger"].get_logger = mock_get_logger
    sys.modules["shared.worker"] = Mock()
    sys.modules["shared.worker.worker"] = Mock()
    sys.modules["shared.worker.worker"].Worker = MockWorker
else:
    # For integration tests, we still need some basic mocking since shared modules don't exist
    # But we'll mock them minimally to allow the worker to import
    sys.modules["shared"] = Mock()
    sys.modules["shared.config"] = Mock()
    sys.modules["shared.config"].config = MockConfig()
    sys.modules["shared.database"] = Mock()
    sys.modules["shared.database.sql"] = Mock()
    sys.modules["shared.database.sql.postgres"] = Mock()
    sys.modules["shared.database.sql.postgres"].PostgresConnection = MockPostgresConnection
    sys.modules["shared.database.vector"] = Mock()
    sys.modules["shared.documents"] = Mock()
    sys.modules["shared.documents.embedding"] = Mock()
    sys.modules["shared.orchestrators"] = Mock()
    sys.modules["shared.llm"] = Mock()
    sys.modules["shared.logger"] = Mock()
    sys.modules["shared.logger"].get_logger = mock_get_logger
    sys.modules["shared.worker"] = Mock()
    sys.modules["shared.worker.worker"] = Mock()
    sys.modules["shared.worker.worker"].Worker = MockWorker


@pytest.fixture
def postgres_container():
    """PostgreSQL test container for integration tests."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture
def rabbitmq_container():
    """RabbitMQ test container for integration tests."""
    from testcontainers.rabbitmq import RabbitMqContainer

    with RabbitMqContainer("rabbitmq:3.12-alpine") as rabbitmq:
        yield rabbitmq


@pytest.fixture
def qdrant_container():
    """Qdrant test container for integration tests."""
    from testcontainers.core.container import DockerContainer

    with (
        DockerContainer("qdrant/qdrant:latest")
        .with_exposed_ports(6333)
        .with_env("QDRANT__SERVICE__HTTP_PORT", "6333") as qdrant
    ):
        qdrant.start()
        # Add convenience methods
        qdrant.host = qdrant.get_container_host_ip()
        qdrant.port = qdrant.get_exposed_port(6333)
        qdrant.get_url = lambda: f"http://{qdrant.host}:{qdrant.port}"
        yield qdrant
