"""RabbitMQ messaging infrastructure - server factory wrapping shared implementations."""

from shared.messaging import RabbitMQPublisher

from .factory import create_rabbitmq_publisher

__all__ = ["RabbitMQPublisher", "create_rabbitmq_publisher"]
