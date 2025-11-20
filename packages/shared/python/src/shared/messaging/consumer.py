"""RabbitMQ consumer base classes for workers."""

import json
import logging
import sys
from typing import Any, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    Base RabbitMQ consumer with connection management.
    
    Handles connection, queue declaration, message consumption,
    and graceful shutdown for worker processes.
    """

    def __init__(
        self,
        rabbitmq_url: str,
        exchange: str = "insighthub",
        exchange_type: str = "topic",
        prefetch_count: int = 1,
    ) -> None:
        """
        Initialize RabbitMQ consumer.

        Args:
            rabbitmq_url: Full RabbitMQ connection URL
            exchange: Exchange name to consume from
            exchange_type: Type of exchange (topic, direct, fanout)
            prefetch_count: Number of messages to prefetch (QoS)
        """
        self.rabbitmq_url = rabbitmq_url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.prefetch_count = prefetch_count
        self.connection: BlockingConnection | None = None
        self.channel: BlockingChannel | None = None
        self.should_stop = False

    def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        logger.info(f"Connecting to RabbitMQ: {self.rabbitmq_url}")
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type, durable=True
        )

        # Set QoS
        self.channel.basic_qos(prefetch_count=self.prefetch_count)

        logger.info("Connected to RabbitMQ successfully")

    def declare_queue(self, queue_name: str, routing_key: str) -> None:
        """
        Declare a queue and bind it to the exchange.

        Args:
            queue_name: Name of the queue
            routing_key: Routing key to bind
        """
        if not self.channel:
            raise RuntimeError("Not connected. Call connect() first.")

        # Declare durable queue
        self.channel.queue_declare(queue=queue_name, durable=True)

        # Bind queue to exchange with routing key
        self.channel.queue_bind(
            exchange=self.exchange, queue=queue_name, routing_key=routing_key
        )

    def consume(
        self,
        queue_name: str,
        callback: Callable[[BlockingChannel, Any, Any, bytes], None],
    ) -> None:
        """
        Start consuming messages from a queue.

        Args:
            queue_name: Name of the queue to consume from
            callback: Callback function to handle messages
        """
        if not self.channel:
            raise RuntimeError("Not connected. Call connect() first.")

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False,
        )

        logger.info(f"Waiting for messages in queue '{queue_name}'. To exit press CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def publish_event(self, routing_key: str, event: Any) -> None:
        """
        Publish an event to RabbitMQ.

        Args:
            routing_key: Routing key for the event
            event: Event object (dataclass or dict)
        """
        if not self.channel:
            raise RuntimeError("Not connected. Call connect() first.")

        # Convert dataclass to dict if needed
        if hasattr(event, "__dict__"):
            event_dict = event.__dict__
        else:
            event_dict = event

        message = json.dumps(event_dict)

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent
        )
        logger.info(f"Published event: {routing_key}")

    def stop(self) -> None:
        """Stop the consumer gracefully."""
        logger.info("Stopping consumer...")
        self.should_stop = True
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
        if self.connection and self.connection.is_open:
            self.connection.close()
        logger.info("Consumer stopped")

    def signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)
