
import pytest
from unittest.mock import MagicMock, patch

from src.main import WikipediaWorker

@pytest.fixture
def wikipedia_worker():
    with patch('src.main.PostgresConnection'), \
         patch('src.main.S3BlobStorage'), \
         patch('src.main.WikipediaFetcher'):
        worker = WikipediaWorker()
        worker.db_connection = MagicMock()
        worker.blob_storage = MagicMock()
        worker.fetcher = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_process_event_success(wikipedia_worker: WikipediaWorker, mocker):
    """
    Test that the wikipedia worker fetches a page and publishes a document.uploaded event.
    """
    # Arrange
    mocker.patch.object(wikipedia_worker, '_publish_status')
    mocker.patch.object(wikipedia_worker, '_publish_document_uploaded_event')
    mocker.patch.object(wikipedia_worker, '_create_document_from_page', return_value=("path/to/file.txt", "doc123"))

    event_data = {
        "workspace_id": "ws1",
        "query": "Test Query",
        "user_id": "user1"
    }
    
    mock_page = {"title": "Test Page", "url": "http://test.com", "content": "Test content", "page_id": "p1"}
    wikipedia_worker.fetcher.search_and_fetch.return_value = [mock_page]

    # Act
    wikipedia_worker.process_event(event_data)

    # Assert
    wikipedia_worker.fetcher.search_and_fetch.assert_called_once_with("Test Query")
    wikipedia_worker._create_document_from_page.assert_called_once_with("ws1", "user1", mock_page)
    wikipedia_worker._publish_document_uploaded_event.assert_called_once_with("ws1", "user1", "doc123", "path/to/file.txt", mock_page)
    
    assert wikipedia_worker._publish_status.call_count == 3
    wikipedia_worker._publish_status.assert_any_call("ws1", "Test Query", "fetching", "Searching Wikipedia...", [])
    wikipedia_worker._publish_status.assert_any_call("ws1", "Test Query", "processing", "Processing 1 pages...", [])
    wikipedia_worker._publish_status.assert_any_call("ws1", "Test Query", "completed", "Created 1 documents", ["doc123"])

