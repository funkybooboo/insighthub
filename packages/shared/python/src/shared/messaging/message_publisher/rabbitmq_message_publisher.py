"""RabbitMQ publisher for publishing events to message queue."""

import json
import logging
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    Publisher for sending events to RabbitMQ.
    
    Used by the server to publish events that workers will consume.
    Supports context manager for automatic connection management.
    
    Example:
        with RabbitMQPublisher(host="rabbitmq", exchange="insighthub") as publisher:
            publisher.publish("document.uploaded", {"document_id": 123})
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "insighthub",
        exchange_type: str = "topic",
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
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.connection: BlockingConnection | None = None
        self.channel: BlockingChannel | None = None

    def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.
        
        Creates a connection and channel, then declares the exchange for event routing.
        """
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange for routing
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type=self.exchange_type,
                durable=True,
            )
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def disconnect(self) -> None:
        """Close connection to RabbitMQ server."""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
        finally:
            self.channel = None
            self.connection = None

    def publish(self, routing_key: str, message: dict[str, Any]) -> None:
        """
        Publish message to RabbitMQ exchange.

        Args:
            routing_key: Routing key for message (e.g., "document.uploaded")
            message: Message payload as dictionary
            
        Raises:
            RuntimeError: If not connected to RabbitMQ
        """
        if not self.channel or not self.channel.is_open:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")
        
        try:
            # Serialize message to JSON
            message_body = json.dumps(message)
            
            # Publish to exchange with persistent delivery
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type="application/json",
                ),
            )
            
            logger.info(
                f"Published event: {routing_key} "
                f"(document_id={message.get('document_id', 'N/A')})"
            )
        except Exception as e:
            logger.error(f"Failed to publish message with routing_key={routing_key}: {e}")
            raise

    def __enter__(self) -> "RabbitMQPublisher":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
