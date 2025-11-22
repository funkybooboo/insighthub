"""Status consumer for bridging RabbitMQ status updates to Socket.IO."""

import json
import os
import threading
from typing import Any, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties

from shared.logger import create_logger

logger = create_logger(__name__)

# Type alias for status callbacks
StatusCallback = Callable[[dict[str, Any]], None]


class StatusConsumer:
    """
    Non-blocking consumer for status updates from RabbitMQ.

    Runs in a background thread and calls callbacks when status updates are received.
    Bridges RabbitMQ events to Socket.IO for real-time UI updates.
    """

    def __init__(
        self,
        rabbitmq_url: str,
        exchange: str,
        on_document_status: StatusCallback,
        on_workspace_status: StatusCallback,
    ) -> None:
        """
        Initialize the status consumer.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            exchange: Exchange name to consume from
            on_document_status: Callback for document status updates
            on_workspace_status: Callback for workspace status updates
        """
        self._rabbitmq_url = rabbitmq_url
        self._exchange = exchange
        self._on_document_status = on_document_status
        self._on_workspace_status = on_workspace_status
        self._connection: BlockingConnection | None = None
        self._channel: BlockingChannel | None = None
        self._consumer_thread: threading.Thread | None = None
        self._should_stop = threading.Event()

    def start(self) -> None:
        """Start the consumer in a background thread."""
        self._consumer_thread = threading.Thread(target=self._run, daemon=True)
        self._consumer_thread.start()
        logger.info("Status consumer thread started")

    def stop(self) -> None:
        """Stop the consumer gracefully."""
        logger.info("Stopping status consumer...")
        self._should_stop.set()

        if self._connection and self._connection.is_open:
            try:
                self._connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

        if self._consumer_thread and self._consumer_thread.is_alive():
            self._consumer_thread.join(timeout=5)

        logger.info("Status consumer stopped")

    def _run(self) -> None:
        """Run the consumer loop."""
        while not self._should_stop.is_set():
            try:
                self._connect_and_consume()
            except Exception as e:
                logger.error(f"Status consumer error: {e}")
                if not self._should_stop.is_set():
                    # Wait before reconnecting
                    self._should_stop.wait(timeout=5)

    def _connect_and_consume(self) -> None:
        """Connect to RabbitMQ and start consuming."""
        logger.info("Connecting to RabbitMQ for status updates...")

        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
        self._channel = self._connection.channel()

        # Declare exchange
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type="topic",
            durable=True,
        )

        # Declare queues for status updates
        # Document status queue
        doc_queue = "status_document_updates"
        self._channel.queue_declare(queue=doc_queue, durable=True)
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=doc_queue,
            routing_key="document.status.updated",
        )

        # Workspace status queue
        ws_queue = "status_workspace_updates"
        self._channel.queue_declare(queue=ws_queue, durable=True)
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=ws_queue,
            routing_key="workspace.status.updated",
        )

        # Set up consumers
        self._channel.basic_qos(prefetch_count=1)

        self._channel.basic_consume(
            queue=doc_queue,
            on_message_callback=self._on_document_message,
            auto_ack=False,
        )

        self._channel.basic_consume(
            queue=ws_queue,
            on_message_callback=self._on_workspace_message,
            auto_ack=False,
        )

        logger.info("Status consumer connected and listening")

        # Start consuming (this blocks until stop is called)
        while not self._should_stop.is_set():
            self._connection.process_data_events(time_limit=1)

    def _on_document_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """Handle incoming document status message."""
        try:
            event_data = json.loads(body.decode("utf-8"))
            logger.debug(f"Received document status: {event_data}")
            self._on_document_status(event_data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing document status: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _on_workspace_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """Handle incoming workspace status message."""
        try:
            event_data = json.loads(body.decode("utf-8"))
            logger.debug(f"Received workspace status: {event_data}")
            self._on_workspace_status(event_data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing workspace status: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def create_status_consumer(
    on_document_status: StatusCallback,
    on_workspace_status: StatusCallback,
) -> StatusConsumer | None:
    """
    Create and start a status consumer if RabbitMQ is configured.

    Args:
        on_document_status: Callback for document status updates
        on_workspace_status: Callback for workspace status updates

    Returns:
        StatusConsumer instance if RabbitMQ is configured, None otherwise
    """
    # Get RabbitMQ configuration from environment
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "")
    rabbitmq_port = os.getenv("RABBITMQ_PORT", "5672")
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")
    exchange = os.getenv("RABBITMQ_EXCHANGE", "insighthub")

    # Check if RabbitMQ is configured
    if not rabbitmq_host:
        logger.info("RabbitMQ not configured, status consumer disabled")
        return None

    rabbitmq_url = f"amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}/"

    try:
        consumer = StatusConsumer(
            rabbitmq_url=rabbitmq_url,
            exchange=exchange,
            on_document_status=on_document_status,
            on_workspace_status=on_workspace_status,
        )
        consumer.start()
        return consumer
    except Exception as e:
        logger.error(f"Failed to create status consumer: {e}")
        return None
