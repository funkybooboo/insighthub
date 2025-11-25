"""Test configuration and fixtures for enricher worker tests."""

import pytest


@pytest.fixture
def postgres_container():
    """PostgreSQL test container for integration tests."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:15-alpine").with_exposed_ports(5432) as postgres:
        yield postgres


@pytest.fixture
def rabbitmq_container():
    """RabbitMQ test container for integration tests."""
    from testcontainers.rabbitmq import RabbitMqContainer

    with RabbitMqContainer("rabbitmq:3.12-alpine").with_exposed_ports(5672) as rabbitmq:
        yield rabbitmq
