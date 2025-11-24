"""Factory for creating message publisher instances."""

from enum import Enum
from typing import Optional

from .message_publisher import MessagePublisher
from .rabbitmq_message_publisher import RabbitMQPublisher


class PublisherType(Enum):
    """Enum for message publisher types."""

    RABBITMQ = "rabbitmq"


def create_message_publisher(
    publisher_type: str,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    exchange: str | None = None,
    exchange_type: str | None = None,
) -> Optional[MessagePublisher]:
    """
    Create a message publisher instance.

    Args:
        publisher_type: Type of publisher ("rabbitmq")
        host: Message broker host (required for rabbitmq)
        port: Message broker port (required for rabbitmq)
        username: Authentication username (required for rabbitmq)
        password: Authentication password (required for rabbitmq)
        exchange: Exchange name (required for rabbitmq)
        exchange_type: Exchange type (required for rabbitmq)

    Returns:
        MessagePublisher if creation succeeds, None otherwise
    """
    try:
        publisher_enum = PublisherType(publisher_type)
    except ValueError:
        return None

    if publisher_enum == PublisherType.RABBITMQ:
        if (
            host is None
            or port is None
            or username is None
            or password is None
            or exchange is None
            or exchange_type is None
        ):
            return None
        return RabbitMQPublisher(
            host=host,
            port=port,
            username=username,
            password=password,
            exchange=exchange,
            exchange_type=exchange_type,
        )

    return None
