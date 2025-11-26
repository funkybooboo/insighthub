"""Base worker class for message queue processing."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from shared.config import AppConfig
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher

logger = logging.getLogger(__name__)


class Worker(ABC):
    """
    Base class for worker processes.

    Provides common functionality for all workers:
    - RabbitMQ connection management via consumer/publisher
    - Message parsing and error handling
    - Event publishing
    - Graceful shutdown

    Subclasses must implement process_message() method.
    """

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ) -> None:
        """
        Initialize worker.

        Args:
            consumer: Message queue consumer instance
            publisher: Message queue publisher instance
            config: Application configuration
        """
        self.consumer = consumer
        self.publisher = publisher
        self.config = config
        self._queue_name: str | None = None

    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process a message from the queue.

        This method must be implemented by subclasses.

        Args:
            message: Parsed message data as dictionary
        """
        pass

    def _on_message(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
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
            message: Dict[str, Any] = json.loads(body)

            logger.info(
                f"Processing message with routing key: {method.routing_key}",
                extra={"routing_key": method.routing_key},
            )

            self.process_message(message)

            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info("Successfully processed message")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def start(self) -> None:
        """Start the worker and begin consuming messages."""
        logger.info("Starting worker")

        if self._queue_name is None:
            raise RuntimeError(
                "Queue name not set. Call consumer.declare_queue() and worker.set_queue_name() before worker.start()"
            )

        try:
            # Start consuming messages
            self.consumer.consume(self._queue_name, self._on_message)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop()
        except Exception as e:
            logger.error(f"Error in worker: {e}", exc_info=True)
            raise

    def stop(self) -> None:
        """Stop the worker gracefully."""
        logger.info("Stopping worker")
        self.consumer.stop()

    def set_queue_name(self, queue_name: str) -> None:
        """
        Set the queue name for consumption.

        Args:
            queue_name: Name of the queue to consume from
        """
        self._queue_name = queue_name
