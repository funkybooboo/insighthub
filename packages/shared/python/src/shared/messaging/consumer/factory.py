"""Factory for creating message consumer instances."""

from enum import Enum
from typing import Optional

from .message_consumer import MessageConsumer
from .rabbitmq_message_consumer import RabbitMQConsumer


class ConsumerType(Enum):
    """Enum for message consumer types."""

    RABBITMQ = "rabbitmq"


def create_message_consumer(
    consumer_type: str,
    rabbitmq_url: str | None = None,
    exchange: str | None = None,
    exchange_type: str | None = None,
    prefetch_count: int | None = None,
) -> Optional[MessageConsumer]:
    """
    Create a message consumer instance.

    Args:
        consumer_type: Type of consumer ("rabbitmq")
        rabbitmq_url: RabbitMQ connection URL (required for rabbitmq)
        exchange: Exchange name (required for rabbitmq)
        exchange_type: Exchange type (required for rabbitmq)
        prefetch_count: Number of messages to prefetch (required for rabbitmq)

    Returns:
        MessageConsumer if creation succeeds, None otherwise
    """
    try:
        consumer_enum = ConsumerType(consumer_type)
    except ValueError:
        return None

    if consumer_enum == ConsumerType.RABBITMQ:
        if (
            rabbitmq_url is None
            or exchange is None
            or exchange_type is None
            or prefetch_count is None
        ):
            return None
        return RabbitMQConsumer(
            rabbitmq_url=rabbitmq_url,
            exchange=exchange,
            exchange_type=exchange_type,
            prefetch_count=prefetch_count,
        )

    return None
