import pytest
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    with PostgresContainer("postgres:13") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def rabbitmq_container() -> RabbitMqContainer:
    with RabbitMqContainer("rabbitmq:3.12-management") as rabbitmq:
        yield rabbitmq


@pytest.fixture(scope="session")
def minio_container() -> MinioContainer:
    with MinioContainer("minio/minio:RELEASE.2023-03-20T20-16-18Z") as minio:
        yield minio
