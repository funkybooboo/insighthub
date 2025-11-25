"""Test configuration and fixtures for embedder worker tests."""

import pytest


@pytest.fixture
def postgres_container():
    """PostgreSQL test container for integration tests."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture
def rabbitmq_container():
    """RabbitMQ test container for integration tests."""
    from testcontainers.core.waiting_utils import wait_for_port
    from testcontainers.rabbitmq import RabbitMqContainer

    with RabbitMqContainer("rabbitmq:3.12-alpine") as rabbitmq:
        # Wait for AMQP port to be available
        wait_for_port(rabbitmq.get_exposed_port(5672), timeout=60)
        yield rabbitmq


@pytest.fixture
def ollama_container():
    """Ollama test container for integration tests."""
    from testcontainers.core.container import DockerContainer

    with (
        DockerContainer("ollama/ollama:latest")
        .with_exposed_ports(11434)
        .with_command("serve")
    ) as ollama:
        ollama.start()
        # Pull the required model
        ollama.exec("ollama pull nomic-embed-text")
        # Add convenience methods
        ollama.get_connection_url = (
            lambda: f"http://{ollama.get_container_host_ip()}:{ollama.get_exposed_port(11434)}"
        )
        yield ollama
