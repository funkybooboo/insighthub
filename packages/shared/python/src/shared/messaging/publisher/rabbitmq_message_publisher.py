"""RabbitMQ publisher implementation."""

import json
from types import TracebackType

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from shared.logger import create_logger
from shared.types.common import PayloadDict

from .message_publisher import MessagePublisher

logger = create_logger(__name__)


class RabbitMQPublisher(MessagePublisher):
    """
    RabbitMQ publisher implementation.

    Used by the server to publish events that workers will consume.
    Supports context manager for automatic connection management.

    Example:
        publisher = RabbitMQPublisher(
            host="rabbitmq",
            port=5672,
            username="guest",
            password="guest",
            exchange="insighthub",
            exchange_type="topic",
        )
        with publisher:
            publisher.publish("document.uploaded", {"document_id": 123})
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        exchange: str,
        exchange_type: str,
    ) -> None:
        """
        Initialize RabbitMQ publisher.

        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            exchange: Exchange name to publish to
            exchange_type: Type of exchange (topic, direct, fanout)
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._connection: BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self) -> None:
        """Establish connection to RabbitMQ server."""
        try:
            credentials = pika.PlainCredentials(self._username, self._password)
            parameters = pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )

            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            self._channel.exchange_declare(
                exchange=self._exchange,
                exchange_type=self._exchange_type,
                durable=True,
            )

            logger.info(
                "Connected to RabbitMQ",
                extra={"host": self._host, "port": self._port},
            )
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", extra={"error": str(e)})
            raise RuntimeError(f"Failed to connect to RabbitMQ: {e}") from e

    def disconnect(self) -> None:
        """Close connection to RabbitMQ server."""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
            if self._connection and self._connection.is_open:
                self._connection.close()
            logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error("Error disconnecting from RabbitMQ", extra={"error": str(e)})
        finally:
            self._channel = None
            self._connection = None

    def publish(self, routing_key: str, message: PayloadDict) -> None:
        """Publish message to RabbitMQ exchange."""
        if not self._channel or not self._channel.is_open:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")

        try:
            message_body = json.dumps(message)

            self._channel.basic_publish(
                exchange=self._exchange,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )

            logger.info("Published event", extra={"routing_key": routing_key})
        except Exception as e:
            logger.error(
                "Failed to publish message",
                extra={"routing_key": routing_key, "error": str(e)},
            )
            raise RuntimeError(f"Failed to publish message: {e}") from e

    def __enter__(self) -> "RabbitMQPublisher":
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
