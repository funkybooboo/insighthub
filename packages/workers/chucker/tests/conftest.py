import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitmqContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:13") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def rabbitmq_container():
    with RabbitmqContainer("rabbitmq:3.8-management") as rabbitmq:
        yield rabbitmq
