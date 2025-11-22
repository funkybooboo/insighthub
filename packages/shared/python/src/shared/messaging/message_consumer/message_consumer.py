"""Abstract message consumer interface."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from shared.types.common import PayloadDict

MessageCallback = Callable[[BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]


class MessageConsumer(ABC):
    """
    Abstract interface for message queue consumers.

    Implementations: RabbitMQConsumer
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to message broker.

        Raises:
            RuntimeError: If connection fails
        """
        pass

    @abstractmethod
    def declare_queue(self, queue_name: str, routing_key: str) -> None:
        """
        Declare a queue and bind it to the exchange.

        Args:
            queue_name: Name of the queue
            routing_key: Routing key to bind

        Raises:
            RuntimeError: If not connected
        """
        pass

    @abstractmethod
    def consume(self, queue_name: str, callback: MessageCallback) -> None:
        """
        Start consuming messages from a queue.

        Args:
            queue_name: Name of the queue to consume from
            callback: Callback function to handle messages

        Raises:
            RuntimeError: If not connected
        """
        pass

    @abstractmethod
    def publish_event(self, routing_key: str, event: PayloadDict) -> None:
        """
        Publish an event to the message broker.

        Args:
            routing_key: Routing key for the event
            event: Event payload as dictionary

        Raises:
            RuntimeError: If not connected
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the consumer gracefully."""
        pass

    @abstractmethod
    def signal_handler(self, signum: int, frame: object) -> None:
        """
        Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        pass
