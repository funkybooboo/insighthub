"""Abstract message publisher interface."""

from abc import ABC, abstractmethod
from types import TracebackType

from shared.types.common import PayloadDict


class MessagePublisher(ABC):
    """
    Abstract interface for message queue publishers.

    Implementations: RabbitMQPublisher
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
    def disconnect(self) -> None:
        """Close connection to message broker."""
        pass

    @abstractmethod
    def publish(self, routing_key: str, message: PayloadDict) -> None:
        """
        Publish message to message broker.

        Args:
            routing_key: Routing key for message (e.g., "document.uploaded")
            message: Message payload as dictionary

        Raises:
            RuntimeError: If not connected
        """
        pass

    def publish_event(self, routing_key: str, event: PayloadDict | None = None, **kwargs: any) -> None:
        """
        Convenience method to publish an event with keyword arguments.

        This allows calling publish_event with either:
        - publish_event("routing.key", {"event_type": "...", ...})
        - publish_event(routing_key="routing.key", event_type="...", ...)

        Args:
            routing_key: Routing key for event
            event: Event payload dict (optional if using kwargs)
            **kwargs: Event fields as keyword arguments
        """
        if event is None:
            event = kwargs
        self.publish(routing_key, event)

    def __enter__(self) -> "MessagePublisher":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.disconnect()
