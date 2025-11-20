"""RabbitMQ consumer for status update events."""

import json
import logging
import os
import threading
from typing import Any, Callable

import pika

logger = logging.getLogger(__name__)


class StatusUpdateConsumer:
    """
    RabbitMQ consumer that listens for status update events and broadcasts them via callbacks.

    This runs in a separate thread to avoid blocking the main Flask application.
    """

    def __init__(
        self,
        rabbitmq_url: str,
        exchange: str,
        on_document_status: Callable[[dict[str, Any]], None],
        on_workspace_status: Callable[[dict[str, Any]], None],
    ):
        """
        Initialize the status update consumer.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            exchange: Exchange name to consume from
            on_document_status: Callback for document status updates
            on_workspace_status: Callback for workspace status updates
        """
        self.rabbitmq_url = rabbitmq_url
        self.exchange = exchange
        self.on_document_status = on_document_status
        self.on_workspace_status = on_workspace_status
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.channel.Channel | None = None
        self.should_stop = False
        self.thread: threading.Thread | None = None

    def connect(self) -> None:
        """Connect to RabbitMQ and set up queues."""
        logger.info(f"Connecting to RabbitMQ: {self.rabbitmq_url}")

        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="topic", durable=True)

        # Declare queue for status updates
        queue_name = "status.updates.server"
        self.channel.queue_declare(queue=queue_name, durable=True)

        # Bind to status update routing keys
        self.channel.queue_bind(
            exchange=self.exchange, queue=queue_name, routing_key="document.status.updated"
        )
        self.channel.queue_bind(
            exchange=self.exchange, queue=queue_name, routing_key="workspace.status.updated"
        )

        logger.info("Connected to RabbitMQ successfully")

    def on_message(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """Handle incoming status update messages."""
        try:
            event_data = json.loads(body)
            routing_key = method.routing_key

            logger.debug(f"Received status update: {routing_key}")

            if routing_key == "document.status.updated":
                self.on_document_status(event_data)
            elif routing_key == "workspace.status.updated":
                self.on_workspace_status(event_data)
            else:
                logger.warning(f"Unknown routing key: {routing_key}")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing status update: {e}", exc_info=True)
            # Negative acknowledgment - message will be requeued
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self) -> None:
        """Start consuming messages in a separate thread."""
        if self.thread and self.thread.is_alive():
            logger.warning("Consumer thread already running")
            return

        def consume():
            try:
                self.connect()
                if self.channel:
                    self.channel.basic_consume(
                        queue="status.updates.server",
                        on_message_callback=self.on_message,
                        auto_ack=False,
                    )
                    logger.info("Started consuming status update events")
                    self.channel.start_consuming()
            except Exception as e:
                logger.error(f"Error in consumer thread: {e}", exc_info=True)

        self.thread = threading.Thread(target=consume, daemon=True)
        self.thread.start()
        logger.info("Status update consumer thread started")

    def stop(self) -> None:
        """Stop consuming messages and close connection."""
        self.should_stop = True
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        logger.info("Status update consumer stopped")


def create_status_consumer(
    on_document_status: Callable[[dict[str, Any]], None],
    on_workspace_status: Callable[[dict[str, Any]], None],
) -> StatusUpdateConsumer | None:
    """
    Create and start a status update consumer.

    Args:
        on_document_status: Callback for document status updates
        on_workspace_status: Callback for workspace status updates

    Returns:
        StatusUpdateConsumer instance or None if RabbitMQ is disabled
    """
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    if not rabbitmq_url:
        logger.warning("RABBITMQ_URL not set, status update consumer disabled")
        return None

    exchange = os.getenv("RABBITMQ_EXCHANGE", "insighthub")

    consumer = StatusUpdateConsumer(
        rabbitmq_url=rabbitmq_url,
        exchange=exchange,
        on_document_status=on_document_status,
        on_workspace_status=on_workspace_status,
    )

    consumer.start()
    return consumer
