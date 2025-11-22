"""Factory for creating message consumer instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

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
) -> Option[MessageConsumer]:
    """
    Create a message consumer instance.

    Args:
        consumer_type: Type of consumer ("rabbitmq")
        rabbitmq_url: RabbitMQ connection URL (required for rabbitmq)
        exchange: Exchange name (required for rabbitmq)
        exchange_type: Exchange type (required for rabbitmq)
        prefetch_count: Number of messages to prefetch (required for rabbitmq)

    Returns:
        Some(MessageConsumer) if creation succeeds, Nothing() otherwise
    """
    try:
        consumer_enum = ConsumerType(consumer_type)
    except ValueError:
        return Nothing()

    if consumer_enum == ConsumerType.RABBITMQ:
        if (
            rabbitmq_url is None
            or exchange is None
            or exchange_type is None
            or prefetch_count is None
        ):
            return Nothing()
        return Some(
            RabbitMQConsumer(
                rabbitmq_url=rabbitmq_url,
                exchange=exchange,
                exchange_type=exchange_type,
                prefetch_count=prefetch_count,
            )
        )

    return Nothing()
