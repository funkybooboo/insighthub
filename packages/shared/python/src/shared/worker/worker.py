"""Base worker class for message queue processing."""

import json
import signal
from abc import ABC, abstractmethod

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from shared.logger import create_logger
from shared.messaging import RabbitMQConsumer
from shared.types.common import PayloadDict

logger = create_logger(__name__)


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
        exchange: str,
        exchange_type: str,
        consume_routing_key: str,
        consume_queue: str,
        prefetch_count: int,
    ) -> None:
        """
        Initialize worker.

        Args:
            worker_name: Name of this worker (for logging)
            rabbitmq_url: RabbitMQ connection URL
            exchange: Exchange name
            exchange_type: Type of exchange (topic, direct, fanout)
            consume_routing_key: Routing key to consume
            consume_queue: Queue name to consume from
            prefetch_count: Number of messages to prefetch
        """
        self._worker_name = worker_name
        self._consume_routing_key = consume_routing_key
        self._consume_queue = consume_queue
        self._consumer = RabbitMQConsumer(
            rabbitmq_url=rabbitmq_url,
            exchange=exchange,
            exchange_type=exchange_type,
            prefetch_count=prefetch_count,
        )

    @abstractmethod
    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process an event from the queue.

        This method must be implemented by subclasses.

        Args:
            event_data: Parsed event data as dictionary
        """
        pass

    def on_message(
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
            event_data: PayloadDict = json.loads(body)

            logger.info(
                "Processing message",
                worker=self._worker_name,
                routing_key=method.routing_key,
            )

            self.process_event(event_data)

            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(
                "Successfully processed message",
                worker=self._worker_name,
            )

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to decode message JSON",
                worker=self._worker_name,
                error=str(e),
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(
                "Error processing message",
                worker=self._worker_name,
                error=str(e),
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def publish_event(self, routing_key: str, event: PayloadDict) -> None:
        """
        Publish an event to RabbitMQ.

        Args:
            routing_key: Routing key for the event
            event: Event payload as dictionary
        """
        self._consumer.publish_event(routing_key, event)
        logger.info(
            "Published event",
            worker=self._worker_name,
            routing_key=routing_key,
        )

    def start(self) -> None:
        """Start the worker."""
        logger.info("Starting worker", worker=self._worker_name)

        signal.signal(signal.SIGINT, self._consumer.signal_handler)
        signal.signal(signal.SIGTERM, self._consumer.signal_handler)

        self._consumer.connect()
        self._consumer.declare_queue(self._consume_queue, self._consume_routing_key)
        self._consumer.consume(self._consume_queue, self.on_message)

    def stop(self) -> None:
        """Stop the worker."""
        logger.info("Stopping worker", worker=self._worker_name)
        self._consumer.stop()
