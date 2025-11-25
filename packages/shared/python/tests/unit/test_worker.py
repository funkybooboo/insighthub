"""Unit tests for worker base class."""

import json
from typing import Any
from unittest.mock import Mock, patch

import pytest
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from shared.types.common import PayloadDict
from shared.worker.worker import Worker


class TestWorker(Worker):
    """Concrete implementation of Worker for testing."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.processed_events: list[PayloadDict] = []
        self.should_fail = False

    def process_event(self, event_data: PayloadDict) -> None:
        """Process event (for testing)."""
        if self.should_fail:
            raise ValueError("Processing failed")
        self.processed_events.append(event_data)


class TestWorkerBase:
    """Test Worker base class."""

    @pytest.fixture
    def worker_kwargs(self) -> dict:
        """Common worker initialization kwargs."""
        return {
            "worker_name": "test_worker",
            "rabbitmq_url": "amqp://localhost",
            "exchange": "test_exchange",
            "exchange_type": "topic",
            "consume_routing_key": "test.routing.key",
            "consume_queue": "test_queue",
            "prefetch_count": 1,
        }

    @pytest.fixture
    def worker(self, worker_kwargs: dict) -> TestWorker:
        """Create a test worker instance."""
        with patch("shared.worker.worker.RabbitMQConsumer"):
            return TestWorker(**worker_kwargs)

    def test_initialization(self, worker_kwargs: dict) -> None:
        """Test worker initialization."""
        with patch("shared.worker.worker.RabbitMQConsumer") as mock_consumer:
            worker = TestWorker(**worker_kwargs)

            assert worker._worker_name == "test_worker"
            assert worker._consume_routing_key == "test.routing.key"
            assert worker._consume_queue == "test_queue"

            # Verify RabbitMQConsumer was created with correct args
            mock_consumer.assert_called_once_with(
                rabbitmq_url="amqp://localhost",
                exchange="test_exchange",
                exchange_type="topic",
                prefetch_count=1,
            )

    @patch("shared.worker.worker.logger")
    def test_on_message_success(self, mock_logger: Mock, worker: TestWorker) -> None:
        """Test successful message processing."""
        # Mock channel and method
        mock_ch = Mock(spec=BlockingChannel)
        mock_method = Mock(spec=Basic.Deliver)
        mock_method.delivery_tag = "tag123"
        mock_method.routing_key = "test.routing.key"
        mock_properties = Mock(spec=BasicProperties)

        # Test message
        event_data = {"action": "test", "data": "value"}
        body = json.dumps(event_data).encode()

        worker.on_message(mock_ch, mock_method, mock_properties, body)

        # Verify event was processed
        assert len(worker.processed_events) == 1
        assert worker.processed_events[0] == event_data

        # Verify message was acknowledged
        mock_ch.basic_ack.assert_called_once_with(delivery_tag="tag123")
        mock_ch.basic_nack.assert_not_called()

    @patch("shared.worker.worker.logger")
    def test_on_message_json_decode_error(self, mock_logger: Mock, worker: TestWorker) -> None:
        """Test message processing with invalid JSON."""
        mock_ch = Mock(spec=BlockingChannel)
        mock_method = Mock(spec=Basic.Deliver)
        mock_method.delivery_tag = "tag123"
        mock_properties = Mock(spec=BasicProperties)

        # Invalid JSON
        body = b"invalid json"

        worker.on_message(mock_ch, mock_method, mock_properties, body)

        # Verify no events were processed
        assert len(worker.processed_events) == 0

        # Verify message was nacked (not requeued)
        mock_ch.basic_nack.assert_called_once_with(delivery_tag="tag123", requeue=False)
        mock_ch.basic_ack.assert_not_called()

    @patch("shared.worker.worker.logger")
    def test_on_message_processing_error(self, mock_logger: Mock, worker: TestWorker) -> None:
        """Test message processing with processing error."""
        mock_ch = Mock(spec=BlockingChannel)
        mock_method = Mock(spec=Basic.Deliver)
        mock_method.delivery_tag = "tag123"
        mock_properties = Mock(spec=BasicProperties)

        # Set worker to fail processing
        worker.should_fail = True

        event_data = {"action": "test"}
        body = json.dumps(event_data).encode()

        worker.on_message(mock_ch, mock_method, mock_properties, body)

        # Verify no events were successfully processed
        assert len(worker.processed_events) == 0

        # Verify message was nacked (requeued)
        mock_ch.basic_nack.assert_called_once_with(delivery_tag="tag123", requeue=True)
        mock_ch.basic_ack.assert_not_called()

    @patch("shared.worker.worker.logger")
    def test_publish_event(self, mock_logger: Mock, worker: TestWorker) -> None:
        """Test event publishing."""
        routing_key = "response.key"
        event = {"status": "completed", "result": "data"}

        worker.publish_event(routing_key, event)  # type: ignore

        # Verify consumer.publish_event was called
        worker._consumer.publish_event.assert_called_once_with(routing_key, event)  # type: ignore

    @patch("shared.worker.worker.logger")
    @patch("signal.signal")
    def test_start(self, mock_signal: Mock, mock_logger: Mock, worker: TestWorker) -> None:
        """Test worker start."""
        worker.start()

        # Verify signal handlers were set
        assert mock_signal.call_count == 2

        # Verify consumer methods were called
        worker._consumer.connect.assert_called_once()  # type: ignore
        worker._consumer.declare_queue.assert_called_once_with("test_queue", "test.routing.key")  # type: ignore
        worker._consumer.consume.assert_called_once_with("test_queue", worker.on_message)  # type: ignore

    @patch("shared.worker.worker.logger")
    def test_stop(self, mock_logger: Mock, worker: TestWorker) -> None:
        """Test worker stop."""
        worker.stop()

        # Verify consumer.stop was called
        worker._consumer.stop.assert_called_once()  # type: ignore

    def test_abstract_method(self) -> None:
        """Test that Worker cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Worker(  # type: ignore
                worker_name="test",
                rabbitmq_url="amqp://localhost",
                exchange="test",
                exchange_type="topic",
                consume_routing_key="test.key",
                consume_queue="test_queue",
                prefetch_count=1,
            )

    def test_process_event_abstract(self, worker_kwargs: dict) -> None:
        """Test that process_event must be implemented."""
        # This would normally raise NotImplementedError, but our test class implements it
        with patch("shared.worker.worker.RabbitMQConsumer"):
            worker = TestWorker(**worker_kwargs)
            # Should not raise an error since we implemented it
            worker.process_event({"test": "data"})
