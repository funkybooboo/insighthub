
import pytest
from unittest.mock import MagicMock, patch

from src.main import IndexerWorker, DocumentIndexedEvent

@pytest.fixture
def indexer_worker():
    with patch('src.main.PostgresConnection'), \
         patch('src.main.QdrantClient'):
        worker = IndexerWorker()
        worker.db_connection = MagicMock()
        worker.qdrant_client = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_process_event_success(indexer_worker: IndexerWorker, mocker):
    """
    Test that the indexer worker processes a document.embedded event successfully
    and publishes a document.indexed event.
    """
    # Arrange
    mocker.patch.object(indexer_worker, '_get_workspace_collection', return_value="test_collection")
    mock_chunks = [{
        "id": "chunk1",
        "embedding": [0.1, 0.2],
        "chunk_text": "text1",
        "chunk_index": 0
    }]
    mocker.patch.object(indexer_worker, '_get_chunks_and_embeddings', return_value=mock_chunks)
    mocker.patch.object(indexer_worker, '_update_document_status')

    event_data = {
        "document_id": "doc123",
        "workspace_id": "ws456",
        "chunk_ids": ["chunk1"],
        "embedding_count": 1,
        "metadata": {},
    }

    # Act
    indexer_worker.process_event(event_data)

    # Assert
    indexer_worker._update_document_status.assert_any_call("doc123", "indexing")
    indexer_worker.qdrant_client.upsert.assert_called_once()
    indexer_worker._update_document_status.assert_any_call("doc123", "ready", {
        "vector_count": 1,
        "collection_name": "test_collection"
    })

    expected_indexed_event = DocumentIndexedEvent(
        document_id="doc123",
        workspace_id="ws456",
        vector_count=1,
        collection_name="test_collection",
        metadata={},
    )
    
    call_args = indexer_worker.publish_event.call_args
    assert call_args is not None
    assert call_args.kwargs['routing_key'] == 'document.indexed'
    assert call_args.kwargs['event']['document_id'] == expected_indexed_event.document_id
    assert call_args.kwargs['event']['vector_count'] == expected_indexed_event.vector_count
    assert call_args.kwargs['event']['collection_name'] == expected_indexed_event.collection_name
