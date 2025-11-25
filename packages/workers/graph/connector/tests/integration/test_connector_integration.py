"""Integration tests for connector worker."""

from unittest.mock import patch

import pytest

from src.main import ConnectorWorker, GraphUpdatedEvent


class TestConnectorWorkerIntegration:
    """Integration tests for ConnectorWorker with mocked dependencies."""

    def test_worker_processes_embedding_created_event_with_placeholders(self) -> None:
        """Test that worker processes embedding.created events with current placeholder implementation."""
        # Setup worker with mocked dependencies since real implementation is TODO
        worker = ConnectorWorker()

        # Mock the methods that aren't implemented yet
        with (
            patch.object(worker, "_update_document_status") as mock_update,
            patch.object(worker, "publish_event") as mock_publish,
        ):
            event_data = {
                "document_id": "test-doc-123",
                "workspace_id": "test-workspace-456",
                "chunk_ids": ["chunk-1", "chunk-2", "chunk-3"],
                "metadata": {"source": "test", "chunk_count": 3},
            }

            # Process the event (currently placeholder implementation)
            worker.process_event(event_data)

            # Verify that the placeholder methods were called with correct parameters
            mock_update.assert_called_once_with(
                "test-doc-123", "graph_connected", {"node_count": 3, "edge_count": 6}
            )

            # Verify graph.updated event was published
            mock_publish.assert_called_once_with(
                routing_key="graph.updated",
                event={
                    "document_id": "test-doc-123",
                    "workspace_id": "test-workspace-456",
                    "node_count": 3,  # len(chunk_ids)
                    "edge_count": 6,  # len(chunk_ids) * 2
                    "metadata": {"source": "test", "chunk_count": 3},
                },
            )

    def test_worker_handles_empty_chunk_ids_with_placeholders(self) -> None:
        """Test that worker handles events with empty chunk_ids gracefully."""
        worker = ConnectorWorker()

        with (
            patch.object(worker, "_update_document_status") as mock_update,
            patch.object(worker, "publish_event") as mock_publish,
        ):
            event_data = {
                "document_id": "test-doc-empty",
                "workspace_id": "test-workspace-456",
                "chunk_ids": [],  # Empty chunks
                "metadata": {"source": "test"},
            }

            # Should not raise an exception
            worker.process_event(event_data)

            # Verify status update with zero counts
            mock_update.assert_called_once_with(
                "test-doc-empty", "graph_connected", {"node_count": 0, "edge_count": 0}
            )

            # Verify event published with zero counts
            mock_publish.assert_called_once_with(
                routing_key="graph.updated",
                event={
                    "document_id": "test-doc-empty",
                    "workspace_id": "test-workspace-456",
                    "node_count": 0,
                    "edge_count": 0,
                    "metadata": {"source": "test"},
                },
            )

    def test_worker_handles_missing_metadata_with_placeholders(self) -> None:
        """Test that worker handles events with missing metadata gracefully."""
        worker = ConnectorWorker()

        with (
            patch.object(worker, "_update_document_status") as mock_update,
            patch.object(worker, "publish_event") as mock_publish,
        ):
            event_data = {
                "document_id": "test-doc-no-meta",
                "workspace_id": "test-workspace-456",
                "chunk_ids": ["chunk-1"],
                # No metadata field - should default to empty dict
            }

            # Should not raise an exception
            worker.process_event(event_data)

            # Verify status update was called
            mock_update.assert_called_once_with(
                "test-doc-no-meta", "graph_connected", {"node_count": 1, "edge_count": 2}
            )

            # Verify event published with empty metadata
            mock_publish.assert_called_once_with(
                routing_key="graph.updated",
                event={
                    "document_id": "test-doc-no-meta",
                    "workspace_id": "test-workspace-456",
                    "node_count": 1,
                    "edge_count": 2,
                    "metadata": {},  # Should be empty dict when missing
                },
            )

    def test_worker_handles_processing_errors_gracefully(self) -> None:
        """Test that worker handles errors during processing and updates status appropriately."""
        worker = ConnectorWorker()

        # Mock methods to simulate failure
        with (
            patch.object(worker, "_update_document_status") as mock_update,
            patch.object(worker, "publish_event") as mock_publish,
        ):
            # Make publish_event raise an exception
            mock_publish.side_effect = Exception("RabbitMQ connection failed")

            event_data = {
                "document_id": "test-doc-error",
                "workspace_id": "test-workspace-456",
                "chunk_ids": ["chunk-1", "chunk-2"],
                "metadata": {"source": "test"},
            }

            # Should raise the exception (current implementation does catch and re-raise)
            with pytest.raises(Exception, match="RabbitMQ connection failed"):
                worker.process_event(event_data)

            # Verify that status was updated to success first, then to failed on error
            assert mock_update.call_count == 2
            mock_update.assert_any_call(
                "test-doc-error", "graph_connected", {"node_count": 2, "edge_count": 4}
            )
            mock_update.assert_any_call(
                "test-doc-error", "failed", {"error": "RabbitMQ connection failed"}
            )

    def test_graph_updated_event_dataclass_serialization(self) -> None:
        """Test that GraphUpdatedEvent can be properly serialized for messaging."""
        event = GraphUpdatedEvent(
            document_id="doc-123",
            workspace_id="ws-456",
            node_count=5,
            edge_count=10,
            metadata={"key": "value"},
        )

        # Test dataclass to dict conversion (used for event publishing)
        from dataclasses import asdict

        event_dict = asdict(event)

        expected = {
            "document_id": "doc-123",
            "workspace_id": "ws-456",
            "node_count": 5,
            "edge_count": 10,
            "metadata": {"key": "value"},
        }

        assert event_dict == expected

        # Verify all fields are serializable (important for message queues)
        import json

        json_str = json.dumps(event_dict)
        assert json.loads(json_str) == expected

    def test_event_processing_preserves_metadata_types(self) -> None:
        """Test that event processing preserves different metadata value types."""
        worker = ConnectorWorker()

        with patch.object(worker, "publish_event") as mock_publish:
            event_data = {
                "document_id": "test-doc-types",
                "workspace_id": "test-workspace-456",
                "chunk_ids": ["chunk-1"],
                "metadata": {
                    "string_val": "test",
                    "int_val": 42,
                    "float_val": 3.14,
                    "bool_val": True,
                    "list_val": ["a", "b", "c"],
                    "dict_val": {"nested": "value"},
                },
            }

            worker.process_event(event_data)

            # Verify metadata is preserved exactly
            expected_metadata = {
                "string_val": "test",
                "int_val": 42,
                "float_val": 3.14,
                "bool_val": True,
                "list_val": ["a", "b", "c"],
                "dict_val": {"nested": "value"},
            }
            mock_publish.assert_called_once_with(
                routing_key="graph.updated",
                event={
                    "document_id": "test-doc-types",
                    "workspace_id": "test-workspace-456",
                    "node_count": 1,
                    "edge_count": 2,
                    "metadata": expected_metadata,
                },
            )
