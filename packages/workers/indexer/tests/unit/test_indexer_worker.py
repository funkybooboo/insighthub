"""Unit tests for indexer worker methods."""

import json
from unittest.mock import Mock, patch

import pytest

from src.main import IndexerWorker


class TestIndexerWorkerMethods:
    """Unit tests for IndexerWorker methods using dummies and mocks."""

    def test_get_workspace_collection_success(self):
        """Test getting workspace collection name successfully."""
        # Create worker with mocked database
        worker = IndexerWorker.__new__(IndexerWorker)  # Create without __init__

        # Mock database connection and cursor
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"rag_collection": "test_collection_123"}
        mock_connection = Mock()
        mock_connection.get_cursor.return_value.__enter__ = Mock(
            return_value=mock_cursor
        )
        mock_connection.get_cursor.return_value.__exit__ = Mock(return_value=None)
        worker.db_connection = mock_connection

        # Test the method
        result = worker._get_workspace_collection("workspace_123")

        assert result == "test_collection_123"
        mock_cursor.execute.assert_called_once_with(
            "SELECT rag_collection FROM workspaces WHERE id = %s", ("workspace_123",)
        )

    def test_get_workspace_collection_not_found(self):
        """Test getting workspace collection when workspace doesn't exist."""
        worker = IndexerWorker.__new__(IndexerWorker)

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_connection = Mock()
        mock_connection.get_cursor.return_value.__enter__ = Mock(
            return_value=mock_cursor
        )
        mock_connection.get_cursor.return_value.__exit__ = Mock(return_value=None)
        worker.db_connection = mock_connection

        result = worker._get_workspace_collection("nonexistent_workspace")

        assert result is None

    def test_get_chunks_and_embeddings_success(self):
        """Test getting chunks and embeddings from database."""
        worker = IndexerWorker.__new__(IndexerWorker)

        mock_cursor = Mock()
        mock_chunks = [
            {
                "id": "chunk1",
                "chunk_text": "text1",
                "chunk_index": 0,
                "embedding": "[0.1, 0.2, 0.3]",
            },
            {
                "id": "chunk2",
                "chunk_text": "text2",
                "chunk_index": 1,
                "embedding": "[0.4, 0.5, 0.6]",
            },
        ]
        mock_cursor.fetchall.return_value = mock_chunks
        mock_connection = Mock()
        mock_connection.get_cursor.return_value.__enter__ = Mock(
            return_value=mock_cursor
        )
        mock_connection.get_cursor.return_value.__exit__ = Mock(return_value=None)
        worker.db_connection = mock_connection

        chunk_ids = ["chunk1", "chunk2"]
        result = worker._get_chunks_and_embeddings(chunk_ids)

        assert len(result) == 2
        assert result[0]["id"] == "chunk1"
        assert result[0]["embedding"] == [0.1, 0.2, 0.3]
        assert result[1]["id"] == "chunk2"
        assert result[1]["embedding"] == [0.4, 0.5, 0.6]

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        assert (
            "SELECT id, chunk_text, chunk_index, embedding FROM document_chunks"
            in call_args[0][0]
        )
        assert call_args[0][1] == (chunk_ids,)

    def test_update_document_status_success(self):
        """Test updating document status successfully."""
        worker = IndexerWorker.__new__(IndexerWorker)

        mock_cursor = Mock()
        mock_connection = Mock()
        mock_connection.connection = Mock()
        mock_connection.get_cursor.return_value.__enter__ = Mock(
            return_value=mock_cursor
        )
        mock_connection.get_cursor.return_value.__exit__ = Mock(return_value=None)
        worker.db_connection = mock_connection

        worker._update_document_status("doc123", "ready", {"vector_count": 5})

        # Check the SQL and parameters
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        expected_sql = "UPDATE documents SET processing_status = %s, processing_metadata = %s, updated_at = NOW() WHERE id = %s"
        assert call_args[0][0] == expected_sql
        assert call_args[0][1] == ("ready", json.dumps({"vector_count": 5}), "doc123")

        # Verify commit was called
        mock_connection.connection.commit.assert_called_once()

    def test_update_document_status_rollback_on_error(self):
        """Test that transaction is rolled back when update fails."""
        worker = IndexerWorker.__new__(IndexerWorker)

        mock_connection = Mock()
        mock_connection.connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_connection.get_cursor.return_value.__enter__ = Mock(
            return_value=mock_cursor
        )
        mock_connection.get_cursor.return_value.__exit__ = Mock(return_value=None)
        worker.db_connection = mock_connection

        with pytest.raises(Exception, match="Database error"):
            worker._update_document_status("doc123", "failed", {"error": "test"})

        # Verify rollback was called
        mock_connection.connection.rollback.assert_called_once()
        mock_connection.connection.commit.assert_not_called()

    @patch("src.main.QdrantClient")
    def test_process_event_successful_indexing(self, mock_qdrant_client):
        """Test successful processing of document.embedded event."""
        worker = IndexerWorker.__new__(IndexerWorker)

        # Mock database methods
        worker._get_workspace_collection = Mock(return_value="test_collection")
        worker._get_chunks_and_embeddings = Mock(
            return_value=[
                {
                    "id": "chunk1",
                    "chunk_text": "text1",
                    "chunk_index": 0,
                    "embedding": [0.1, 0.2, 0.3],
                },
                {
                    "id": "chunk2",
                    "chunk_text": "text2",
                    "chunk_index": 1,
                    "embedding": [0.4, 0.5, 0.6],
                },
            ]
        )
        worker._update_document_status = Mock()
        worker.publish_event = Mock()

        # Mock Qdrant client
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client
        worker.qdrant_client = mock_client

        # Test event data
        event_data = {
            "document_id": "doc123",
            "workspace_id": "ws456",
            "chunk_ids": ["chunk1", "chunk2"],
            "metadata": {"source": "test"},
        }

        # Process the event
        worker.process_event(event_data)

        # Verify workspace collection was retrieved
        worker._get_workspace_collection.assert_called_once_with("ws456")

        # Verify chunks were retrieved
        worker._get_chunks_and_embeddings.assert_called_once_with(["chunk1", "chunk2"])

        # Verify Qdrant upsert was called
        mock_client.upsert.assert_called_once()
        upsert_call = mock_client.upsert.call_args
        assert upsert_call[1]["collection_name"] == "test_collection"
        points = upsert_call[1]["points"]
        assert len(points) == 2
        assert points[0].id == "chunk1"
        assert points[0].vector == [0.1, 0.2, 0.3]
        assert points[1].id == "chunk2"
        assert points[1].vector == [0.4, 0.5, 0.6]

        # Verify document status was updated to ready
        worker._update_document_status.assert_called_with(
            "doc123", "ready", {"vector_count": 2, "collection_name": "test_collection"}
        )

        # Verify event was published
        worker.publish_event.assert_called_once()
        publish_call = worker.publish_event.call_args
        # publish_event(routing_key, event) - called with keyword args
        routing_key = publish_call.kwargs["routing_key"]
        published_event = publish_call.kwargs["event"]
        assert routing_key == "document.indexed"
        assert published_event["document_id"] == "doc123"
        assert published_event["workspace_id"] == "ws456"
        assert published_event["vector_count"] == 2
        assert published_event["collection_name"] == "test_collection"
        assert published_event["metadata"] == {"source": "test"}

    @patch("src.main.QdrantClient")
    def test_process_event_no_embeddings_fails(self, mock_qdrant_client):
        """Test processing fails when no embeddings are found."""
        worker = IndexerWorker.__new__(IndexerWorker)

        # Mock database methods
        worker._get_workspace_collection = Mock(return_value="test_collection")
        worker._get_chunks_and_embeddings = Mock(
            return_value=[
                {
                    "id": "chunk1",
                    "chunk_text": "text1",
                    "chunk_index": 0,
                    "embedding": None,
                },  # No embedding
            ]
        )
        worker._update_document_status = Mock()
        worker.publish_event = Mock()

        # Mock Qdrant client
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client
        worker.qdrant_client = mock_client

        event_data = {
            "document_id": "doc123",
            "workspace_id": "ws456",
            "chunk_ids": ["chunk1"],
            "metadata": {},
        }

        worker.process_event(event_data)

        # Verify Qdrant upsert was not called (no valid embeddings)
        mock_client.upsert.assert_not_called()

        # Verify document status was updated (called twice: indexing -> failed)
        assert worker._update_document_status.call_count == 2
        # Check the final call (failed status)
        final_call = worker._update_document_status.call_args_list[1]
        assert final_call[0][0] == "doc123"
        assert final_call[0][1] == "failed"
        assert final_call[0][2] == {"error": "No embeddings found to index"}

        # Verify no event was published
        worker.publish_event.assert_not_called()

    @patch("src.main.QdrantClient")
    @patch.object(IndexerWorker, "_get_workspace_collection", return_value=None)
    @patch.object(IndexerWorker, "_update_document_status")
    @patch.object(IndexerWorker, "publish_event")
    def test_process_event_missing_workspace_fails(
        self,
        mock_publish_event,
        mock_update_status,
        mock_get_collection,
        mock_qdrant_client,
    ):
        """Test processing fails when workspace collection is not found."""
        worker = IndexerWorker.__new__(IndexerWorker)

        # Mock Qdrant client
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client
        worker.qdrant_client = mock_client

        event_data = {
            "document_id": "doc123",
            "workspace_id": "nonexistent_ws",
            "chunk_ids": ["chunk1"],
            "metadata": {},
        }

        # The process_event method catches exceptions, updates status, and re-raises
        with pytest.raises(
            ValueError, match="No collection name found for workspace nonexistent_ws"
        ):
            worker.process_event(event_data)

        # Verify workspace collection was attempted
        mock_get_collection.assert_called_once_with("nonexistent_ws")

        # Verify document status was updated to failed
        mock_update_status.assert_called_once_with(
            "doc123",
            "failed",
            {"error": "No collection name found for workspace nonexistent_ws"},
        )

        # Verify no event was published
        mock_publish_event.assert_not_called()
