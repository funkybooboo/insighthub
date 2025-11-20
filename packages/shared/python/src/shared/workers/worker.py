import json
import logging
import signal
from abc import ABC, abstractmethod
from typing import Any

from pika.adapters.blocking_connection import BlockingChannel
from shared.messaging import RabbitMQConsumer

logger = logging.getLogger(__name__)

class Worker(ABC):
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
