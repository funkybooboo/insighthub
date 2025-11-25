import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    with PostgresContainer("postgres:13") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def rabbitmq_container() -> DockerContainer:
    with DockerContainer("rabbitmq:3.12-management").with_network_mode(
        "host"
    ) as rabbitmq:
        yield rabbitmq


@pytest.fixture(scope="session")
def minio_container() -> MinioContainer:
    with MinioContainer("minio/minio:RELEASE.2022-03-17T06-34-49Z") as minio:
        yield minio
