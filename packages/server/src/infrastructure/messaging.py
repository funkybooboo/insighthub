"""Factory for creating message publisher instances using server configuration."""

from shared.messaging import RabbitMQPublisher


def create_rabbitmq_publisher() -> RabbitMQPublisher | None:
    """
    Create a RabbitMQ publisher instance based on server configuration.

    RabbitMQ is optional - returns None if not configured.
    To enable RabbitMQ, add these environment variables:
        RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD,
        RABBITMQ_EXCHANGE, RABBITMQ_EXCHANGE_TYPE

    Returns:
        RabbitMQPublisher instance if configured, None otherwise
    """
    # RabbitMQ is optional - return None if not configured
    # When RabbitMQ config is added to config.py, this function will be updated
    return None
