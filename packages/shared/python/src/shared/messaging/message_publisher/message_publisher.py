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
