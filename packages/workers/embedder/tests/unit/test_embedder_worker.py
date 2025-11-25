
import pytest
from unittest.mock import MagicMock, patch

from src.main import EmbedderWorker, DocumentEmbeddedEvent

@pytest.fixture
def embedder_worker():
    with patch('src.main.PostgresConnection'), \
         patch('src.main.create_embedding_encoder'):
        worker = EmbedderWorker()
        worker.db_connection = MagicMock()
        worker.embedding_encoder = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_process_event_success(embedder_worker: EmbedderWorker, mocker):
    """
    Test that the embedder worker processes a document.chunked event successfully
    and publishes a document.embedded event.
    """
    # Arrange
    mocker.patch.object(embedder_worker, '_get_chunk_texts', return_value=["text1", "text2"])
    mocker.patch.object(embedder_worker, '_store_embeddings')
    mocker.patch.object(embedder_worker, '_update_document_status')

    event_data = {
        "document_id": "doc123",
        "workspace_id": "ws456",
        "chunk_ids": ["chunk1", "chunk2"],
        "chunk_count": 2,
        "metadata": {},
    }

    mock_embeddings = [[0.1, 0.2], [0.3, 0.4]]
    embedder_worker.embedding_encoder.encode.return_value = MagicMock(unwrap=lambda: mock_embeddings)
    embedder_worker.embedding_encoder.get_dimension.return_value = 2

    # Act
    embedder_worker.process_event(event_data)

    # Assert
    embedder_worker._update_document_status.assert_any_call("doc123", "embedding")
    embedder_worker.embedding_encoder.encode.assert_called_once_with(["text1", "text2"])
    embedder_worker._store_embeddings.assert_called_once_with(["chunk1", "chunk2"], mock_embeddings)
    embedder_worker._update_document_status.assert_any_call("doc123", "embedded", {
        "embedding_count": 2,
        "embedding_dimension": 2
    })

    expected_embedded_event = DocumentEmbeddedEvent(
        document_id="doc123",
        workspace_id="ws456",
        chunk_ids=["chunk1", "chunk2"],
        embedding_count=2,
        metadata={},
    )
    
    call_args = embedder_worker.publish_event.call_args
    assert call_args is not None
    assert call_args.kwargs['routing_key'] == 'document.embedded'
    assert call_args.kwargs['event']['document_id'] == expected_embedded_event.document_id
    assert call_args.kwargs['event']['embedding_count'] == expected_embedded_event.embedding_count

