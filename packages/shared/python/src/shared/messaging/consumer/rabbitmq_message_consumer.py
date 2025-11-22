"""RabbitMQ consumer implementation."""

import json
import sys

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from shared.logger import create_logger
from shared.types.common import PayloadDict

from .message_consumer import MessageCallback, MessageConsumer

logger = create_logger(__name__)


class RabbitMQConsumer(MessageConsumer):
    """
    RabbitMQ consumer implementation.

    Handles connection, queue declaration, message consumption,
    and graceful shutdown for worker processes.

    Example:
        consumer = RabbitMQConsumer(
            rabbitmq_url="amqp://guest:guest@localhost:5672/",
            exchange="insighthub",
            exchange_type="topic",
            prefetch_count=1,
        )
        consumer.connect()
        consumer.declare_queue("document_queue", "document.#")
        consumer.consume("document_queue", on_message_callback)
    """

    def __init__(
        self,
        rabbitmq_url: str,
        exchange: str,
        exchange_type: str,
        prefetch_count: int,
    ) -> None:
        """
        Initialize RabbitMQ consumer.

        Args:
            rabbitmq_url: Full RabbitMQ connection URL
            exchange: Exchange name to consume from
            exchange_type: Type of exchange (topic, direct, fanout)
            prefetch_count: Number of messages to prefetch (QoS)
        """
        self._rabbitmq_url = rabbitmq_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._prefetch_count = prefetch_count
        self._connection: BlockingConnection | None = None
        self._channel: BlockingChannel | None = None
        self._should_stop = False

    def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        logger.info("Connecting to RabbitMQ", url=self._rabbitmq_url)

        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
        self._channel = self._connection.channel()

        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type=self._exchange_type,
            durable=True,
        )

        self._channel.basic_qos(prefetch_count=self._prefetch_count)

        logger.info("Connected to RabbitMQ successfully")

    def declare_queue(self, queue_name: str, routing_key: str) -> None:
        """Declare a queue and bind it to the exchange."""
        if not self._channel:
            raise RuntimeError("Not connected. Call connect() first.")

        self._channel.queue_declare(queue=queue_name, durable=True)

        self._channel.queue_bind(
            exchange=self._exchange,
            queue=queue_name,
            routing_key=routing_key,
        )

        logger.info(
            "Queue declared and bound",
            queue=queue_name,
            routing_key=routing_key,
        )

    def consume(self, queue_name: str, callback: MessageCallback) -> None:
        """Start consuming messages from a queue."""
        if not self._channel:
            raise RuntimeError("Not connected. Call connect() first.")

        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False,
        )

        logger.info("Starting to consume messages", queue=queue_name)

        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def publish_event(self, routing_key: str, event: PayloadDict) -> None:
        """Publish an event to RabbitMQ."""
        if not self._channel:
            raise RuntimeError("Not connected. Call connect() first.")

        message = json.dumps(event)

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

        logger.info("Published event", routing_key=routing_key)

    def stop(self) -> None:
        """Stop the consumer gracefully."""
        logger.info("Stopping consumer...")
        self._should_stop = True

        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()

        if self._connection and self._connection.is_open:
            self._connection.close()

        logger.info("Consumer stopped")

    def signal_handler(self, signum: int, frame: object) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal", signal=signum)
        self.stop()
        sys.exit(0)
