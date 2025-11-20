"""Factory for creating RabbitMQ publisher instances."""

import os

from shared.messaging import RabbitMQPublisher


def create_rabbitmq_publisher() -> RabbitMQPublisher | None:
    """
    Create RabbitMQ publisher from environment variables.

    Returns:
        RabbitMQPublisher instance or None if RabbitMQ is disabled

    Environment Variables:
        RABBITMQ_ENABLED: Enable/disable RabbitMQ (default: false)
        RABBITMQ_HOST: RabbitMQ host (default: localhost)
        RABBITMQ_PORT: RabbitMQ port (default: 5672)
        RABBITMQ_USER: RabbitMQ username (default: guest)
        RABBITMQ_PASS: RabbitMQ password (default: guest)
        RABBITMQ_EXCHANGE: Exchange name (default: insighthub)

    TODO: Add connection retry logic
    TODO: Add health check method
    TODO: Add connection pooling for high throughput
    TODO: Add metrics for published messages
    """
    # Check if RabbitMQ is enabled
    rabbitmq_enabled = os.getenv("RABBITMQ_ENABLED", "false").lower() == "true"

    if not rabbitmq_enabled:
        return None

    # Get configuration from environment
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    username = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASS", "guest")
    exchange = os.getenv("RABBITMQ_EXCHANGE", "insighthub")

    # Create publisher instance
    publisher = RabbitMQPublisher(
        host=host,
        port=port,
        username=username,
        password=password,
        exchange=exchange,
    )

    # TODO: Connect to RabbitMQ (add connection logic in publisher.connect())
    # publisher.connect()

    return publisher
