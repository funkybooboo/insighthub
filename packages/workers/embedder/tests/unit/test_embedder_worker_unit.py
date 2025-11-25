"""Unit tests for EmbedderWorker using dummy implementations."""

from unittest.mock import MagicMock

import pytest
from dummies import DummyEmbeddingEncoder, DummyPostgresConnection

from main import EmbedderWorker


class TestEmbedderWorkerUnit:
    """Unit tests for EmbedderWorker methods."""

    def test_get_chunk_texts_success(self):
        """Test successful retrieval of chunk texts."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)  # Create without __init__
        worker.db_connection = DummyPostgresConnection()

        # Override the get_cursor method to return our mock
        def mock_get_cursor(as_dict=False):
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                {"id": "chunk-1", "chunk_text": "First chunk text"},
                {"id": "chunk-2", "chunk_text": "Second chunk text"},
            ]
            # Make it a context manager
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=None)
            return mock_cursor

        worker.db_connection.get_cursor = mock_get_cursor

        # Test
        chunk_ids = ["chunk-1", "chunk-2"]
        result = worker._get_chunk_texts(chunk_ids)

        # Verify
        assert result == ["First chunk text", "Second chunk text"]

    def test_get_chunk_texts_partial_missing(self):
        """Test retrieval when some chunks are missing."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        # Override the get_cursor method to return our mock
        def mock_get_cursor(as_dict=False):
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                {"id": "chunk-1", "chunk_text": "First chunk text"}
                # chunk-2 is missing
            ]
            # Make it a context manager
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=None)
            return mock_cursor

        worker.db_connection.get_cursor = mock_get_cursor

        # Test
        chunk_ids = ["chunk-1", "chunk-2", "chunk-3"]
        result = worker._get_chunk_texts(chunk_ids)

        # Verify - only returns texts for chunks that exist
        assert result == ["First chunk text"]

    def test_get_chunk_texts_empty_result(self):
        """Test retrieval when no chunks exist."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        worker.db_connection.get_cursor = MagicMock(return_value=mock_cursor)

        # Test
        chunk_ids = ["chunk-1", "chunk-2"]
        result = worker._get_chunk_texts(chunk_ids)

        # Verify
        assert result == []

    def test_store_embeddings_success(self):
        """Test successful storage of embeddings."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        # Mock the get_cursor method
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        worker.db_connection.get_cursor = MagicMock(return_value=mock_cursor)
        worker.db_connection.connection = MagicMock()

        # Test
        chunk_ids = ["chunk-1", "chunk-2"]
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        worker._store_embeddings(chunk_ids, embeddings)

        # Verify
        worker.db_connection.get_cursor.assert_called_once()
        worker.db_connection.connection.commit.assert_called_once()

    def test_update_document_status_success(self):
        """Test successful document status update."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        # Mock the get_cursor method
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        worker.db_connection.get_cursor = MagicMock(return_value=mock_cursor)
        worker.db_connection.connection = MagicMock()

        # Test
        worker._update_document_status("doc-1", "embedded", {"count": 5})

        # Verify
        worker.db_connection.get_cursor.assert_called_once()
        worker.db_connection.connection.commit.assert_called_once()

    def test_update_document_status_no_metadata(self):
        """Test document status update without metadata."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        # Mock the get_cursor method
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        worker.db_connection.get_cursor = MagicMock(return_value=mock_cursor)
        worker.db_connection.connection = MagicMock()

        # Test
        worker._update_document_status("doc-1", "failed")

        # Verify
        worker.db_connection.get_cursor.assert_called_once()
        worker.db_connection.connection.commit.assert_called_once()

    def test_process_event_success(self):
        """Test successful processing of document.chunked event."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()
        worker.embedding_encoder = DummyEmbeddingEncoder()

        # Mock methods
        worker._update_document_status = MagicMock()
        worker._get_chunk_texts = MagicMock(
            return_value=["chunk text 1", "chunk text 2"]
        )
        worker._store_embeddings = MagicMock()
        worker.publish_event = MagicMock()

        # Test event
        event_data = {
            "document_id": "doc-1",
            "workspace_id": "ws-1",
            "chunk_ids": ["chunk-1", "chunk-2"],
            "chunk_count": 2,
            "metadata": {"source": "test"},
        }

        worker.process_event(event_data)

        # Verify
        worker._update_document_status.assert_any_call("doc-1", "embedding")
        worker._get_chunk_texts.assert_called_once_with(["chunk-1", "chunk-2"])
        worker._store_embeddings.assert_called_once()
        worker._update_document_status.assert_any_call(
            "doc-1", "embedded", {"embedding_count": 2, "embedding_dimension": 384}
        )
        worker.publish_event.assert_called_once()

    def test_process_event_no_chunks_found(self):
        """Test processing when no chunk texts are found."""
        # Setup
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()
        worker.embedding_encoder = DummyEmbeddingEncoder()

        worker._update_document_status = MagicMock()
        worker._get_chunk_texts = MagicMock(return_value=[])
        worker.publish_event = MagicMock()

        event_data = {
            "document_id": "doc-1",
            "workspace_id": "ws-1",
            "chunk_ids": ["chunk-1"],
            "chunk_count": 1,
            "metadata": {},
        }

        # Test - should raise ValueError
        with pytest.raises(ValueError, match="No chunk texts found"):
            worker.process_event(event_data)

        # Verify error handling
        worker._update_document_status.assert_any_call(
            "doc-1", "failed", {"error": "No chunk texts found for document doc-1"}
        )
