import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:13") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def rabbitmq_container():
    with DockerContainer("rabbitmq:3.12-management").with_network_mode(
        "host"
    ) as rabbitmq:
        yield rabbitmq


@pytest.fixture(scope="session")
def minio_container():
    with DockerContainer("minio/minio:RELEASE.2022-03-17T06-34-49Z") as minio:
        minio.with_env("MINIO_ROOT_USER", "minioadmin")
        minio.with_env("MINIO_ROOT_PASSWORD", "minioadmin")
        minio.with_exposed_ports(9000, 9001)
        minio.with_command("minio server /data")
        yield minio
