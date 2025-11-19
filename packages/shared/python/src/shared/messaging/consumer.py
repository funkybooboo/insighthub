"""RabbitMQ consumer base classes for workers."""

import json
import logging
import signal
import sys
from abc import ABC, abstractmethod
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


class WorkerBase(ABC):
    """
    Base class for worker processes.
    
    Provides common functionality for all workers:
    - RabbitMQ connection management
    - Signal handling for graceful shutdown
    - Message parsing and error handling
    - Event publishing
    
    Subclasses must implement process_event() method.
    """

    def __init__(
        self,
        worker_name: str,
        rabbitmq_url: str,
        exchange: str = "insighthub",
        consume_routing_key: str = "",
        consume_queue: str = "",
        prefetch_count: int = 1,
    ) -> None:
        """
        Initialize worker.

        Args:
            worker_name: Name of this worker (for logging)
            rabbitmq_url: RabbitMQ connection URL
            exchange: Exchange name
            consume_routing_key: Routing key to consume
            consume_queue: Queue name to consume from
            prefetch_count: Number of messages to prefetch
        """
        self.worker_name = worker_name
        self.consume_routing_key = consume_routing_key
        self.consume_queue = consume_queue
        self.consumer = RabbitMQConsumer(
            rabbitmq_url=rabbitmq_url,
            exchange=exchange,
            prefetch_count=prefetch_count,
        )

    @abstractmethod
    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process an event from the queue.
        
        This method must be implemented by subclasses.

        Args:
            event_data: Parsed event data as dictionary
            
        Raises:
            Exception: If processing fails
        """
        pass

    def on_message(
        self, ch: BlockingChannel, method: Any, properties: Any, body: bytes
    ) -> None:
        """
        Handle incoming message.

        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body (JSON bytes)
        """
        try:
            # Parse event
            event_data = json.loads(body)
            
            logger.info(
                f"[{self.worker_name}] Processing message: "
                f"routing_key={method.routing_key}"
            )

            # Process event (implemented by subclass)
            self.process_event(event_data)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(f"[{self.worker_name}] Successfully processed message")

        except Exception as e:
            logger.error(
                f"[{self.worker_name}] Error processing message: {e}",
                exc_info=True,
            )
            # Reject and requeue message on error
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self) -> None:
        """Start the worker."""
        logger.info(f"Starting {self.worker_name} worker")

        # Register signal handlers
        signal.signal(signal.SIGINT, self.consumer.signal_handler)
        signal.signal(signal.SIGTERM, self.consumer.signal_handler)

        # Connect to RabbitMQ
        self.consumer.connect()

        # Declare queue and bind
        self.consumer.declare_queue(self.consume_queue, self.consume_routing_key)

        # Start consuming
        self.consumer.consume(self.consume_queue, self.on_message)
