
import pytest
from unittest.mock import MagicMock, patch

from src.main import ChuckerWorker, DocumentChunkedEvent

@pytest.fixture
def chucker_worker():
    with patch('src.main.PostgresConnection'), \
         patch('src.main.create_chunker'):
        worker = ChuckerWorker()
        worker.db_connection = MagicMock()
        worker.chunker = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_process_event_success(chucker_worker: ChuckerWorker, mocker):
    """
    Test that the chucker worker processes a document.parsed event successfully
    and publishes a document.chunked event.
    """
    # Arrange
    mocker.patch.object(chucker_worker, '_get_parsed_text', return_value="This is a test text for chunking.")
    mocker.patch.object(chucker_worker, '_store_chunks', return_value=["chunk1", "chunk2"])
    mocker.patch.object(chucker_worker, '_update_document_status')

    event_data = {
        "document_id": "doc123",
        "workspace_id": "ws456",
        "content_type": "text/plain",
        "text_length": 33,
        "metadata": {},
    }

    mock_chunks = [MagicMock(), MagicMock()]
    chucker_worker.chunker.chunk.return_value = mock_chunks
    
    # Act
    chucker_worker.process_event(event_data)

    # Assert
    chucker_worker._update_document_status.assert_any_call("doc123", "chunking")
    chucker_worker.chunker.chunk.assert_called_once()
    chucker_worker._store_chunks.assert_called_once_with("doc123", mock_chunks)
    chucker_worker._update_document_status.assert_any_call("doc123", "chunked", {"chunk_count": 2})

    expected_chunked_event = DocumentChunkedEvent(
        document_id="doc123",
        workspace_id="ws456",
        chunk_ids=["chunk1", "chunk2"],
        chunk_count=2,
        metadata={},
    )
    
    call_args = chucker_worker.publish_event.call_args
    assert call_args is not None
    assert call_args.kwargs['routing_key'] == 'document.chunked'
    assert call_args.kwargs['event']['document_id'] == expected_chunked_event.document_id
    assert call_args.kwargs['event']['chunk_count'] == expected_chunked_event.chunk_count
    assert call_args.kwargs['event']['chunk_ids'] == expected_chunked_event.chunk_ids
