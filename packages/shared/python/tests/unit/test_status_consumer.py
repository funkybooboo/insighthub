"""Unit tests for StatusUpdateConsumer."""

import json
from unittest.mock import Mock, patch

import pytest

from packages.shared.python.src.shared.messaging.status_consumer import (
    StatusUpdateConsumer,
    create_status_consumer,
)


class TestStatusUpdateConsumer:
    """Tests for StatusUpdateConsumer class."""

    @pytest.fixture
    def mock_connection(self):
        """Create mock RabbitMQ connection."""
        connection = Mock()
        channel = Mock()
        connection.channel.return_value = channel
        return connection, channel

    @pytest.fixture
    def consumer(self, mock_connection):
        """Create StatusUpdateConsumer instance with mocked connection."""
        _, channel = mock_connection

        on_document_status = Mock()
        on_workspace_status = Mock()

        consumer = StatusUpdateConsumer(
            rabbitmq_url="amqp://test:test@localhost:5672/",
            exchange="test_exchange",
            on_document_status=on_document_status,
            on_workspace_status=on_workspace_status,
        )

        return consumer, on_document_status, on_workspace_status

    @patch("src.infrastructure.messaging.status_consumer.pika.BlockingConnection")
    def test_connect_success(self, mock_blocking_connection, consumer):
        """Test successful connection to RabbitMQ."""
        consumer_instance, _, _ = consumer
        mock_connection = Mock()
        mock_channel = Mock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection.return_value = mock_connection

        consumer_instance.connect()

        # Verify connection was created
        mock_blocking_connection.assert_called_once()

        # Verify exchange was declared
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test_exchange", exchange_type="topic", durable=True
        )

        # Verify queue was declared
        mock_channel.queue_declare.assert_called_once_with(
            queue="status.updates.server", durable=True
        )

        # Verify bindings were created
        assert mock_channel.queue_bind.call_count == 2

    def test_on_message_document_status(self, consumer):
        """Test handling document status update message."""
        consumer_instance, on_document_status, _ = consumer

        # Create mock message
        event_data = {
            "document_id": 123,
            "user_id": 456,
            "status": "processing",
            "filename": "test.pdf",
        }

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.routing_key = "document.status.updated"
        mock_method.delivery_tag = "tag123"
        mock_properties = Mock()
        body = json.dumps(event_data).encode()

        # Call on_message
        consumer_instance.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify callback was called
        on_document_status.assert_called_once_with(event_data)

        # Verify message was acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag="tag123")

    def test_on_message_workspace_status(self, consumer):
        """Test handling workspace status update message."""
        consumer_instance, _, on_workspace_status = consumer

        # Create mock message
        event_data = {
            "workspace_id": 789,
            "user_id": 456,
            "status": "ready",
            "name": "My Workspace",
        }

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.routing_key = "workspace.status.updated"
        mock_method.delivery_tag = "tag456"
        mock_properties = Mock()
        body = json.dumps(event_data).encode()

        # Call on_message
        consumer_instance.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify callback was called
        on_workspace_status.assert_called_once_with(event_data)

        # Verify message was acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag="tag456")

    def test_on_message_invalid_json(self, consumer):
        """Test handling message with invalid JSON."""
        consumer_instance, on_document_status, _ = consumer

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.routing_key = "document.status.updated"
        mock_method.delivery_tag = "tag789"
        mock_properties = Mock()
        body = b"invalid json"

        # Call on_message
        consumer_instance.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify callback was not called
        on_document_status.assert_not_called()

        # Verify message was negatively acknowledged (requeued)
        mock_channel.basic_nack.assert_called_once_with(delivery_tag="tag789", requeue=True)

    def test_on_message_unknown_routing_key(self, consumer):
        """Test handling message with unknown routing key."""
        consumer_instance, on_document_status, on_workspace_status = consumer

        event_data = {"some": "data"}

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.routing_key = "unknown.routing.key"
        mock_method.delivery_tag = "tag999"
        mock_properties = Mock()
        body = json.dumps(event_data).encode()

        # Call on_message
        consumer_instance.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify callbacks were not called
        on_document_status.assert_not_called()
        on_workspace_status.assert_not_called()

        # Verify message was acknowledged anyway
        mock_channel.basic_ack.assert_called_once_with(delivery_tag="tag999")

    @patch.dict("os.environ", {"RABBITMQ_URL": "amqp://test:test@localhost:5672/"})
    @patch("src.infrastructure.messaging.status_consumer.StatusUpdateConsumer")
    def test_create_status_consumer_with_url(self, mock_consumer_class):
        """Test creating status consumer when RABBITMQ_URL is set."""
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer

        on_doc = Mock()
        on_ws = Mock()

        result = create_status_consumer(
            on_document_status=on_doc,
            on_workspace_status=on_ws,
        )

        # Verify consumer was created
        mock_consumer_class.assert_called_once()

        # Verify start was called
        mock_consumer.start.assert_called_once()

        # Verify result is the consumer
        assert result == mock_consumer

    @patch.dict("os.environ", {}, clear=True)
    def test_create_status_consumer_without_url(self):
        """Test creating status consumer when RABBITMQ_URL is not set."""
        on_doc = Mock()
        on_ws = Mock()

        result = create_status_consumer(
            on_document_status=on_doc,
            on_workspace_status=on_ws,
        )

        # Verify None is returned
        assert result is None
