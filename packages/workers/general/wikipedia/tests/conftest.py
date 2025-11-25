import pytest
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer


@pytest.fixture(scope="function")
def postgres_container():
    """PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:15-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def rabbitmq_container():
    """RabbitMQ container for integration tests."""
    with RabbitMqContainer("rabbitmq:3.12-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def minio_container():
    """MinIO container for integration tests."""
    with MinioContainer("minio/minio:RELEASE.2023-03-20T20-16-18Z") as container:
        yield container
