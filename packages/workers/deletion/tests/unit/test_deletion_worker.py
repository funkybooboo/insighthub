
import pytest
from unittest.mock import MagicMock, patch

from src.main import DeletionWorker

@pytest.fixture
def deletion_worker():
    with patch('src.main.PostgresConnection'), \
         patch('src.main.QdrantClient'), \
         patch('src.main.S3BlobStorage'):
        worker = DeletionWorker()
        worker.db_connection = MagicMock()
        worker.qdrant_client = MagicMock()
        worker.blob_storage = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_handle_workspace_deletion(deletion_worker: DeletionWorker, mocker):
    """
    Test that the deletion worker handles a workspace deletion event successfully.
    """
    # Arrange
    mocker.patch.object(deletion_worker, '_get_workspace_collection', return_value="test_collection")
    mocker.patch.object(deletion_worker, '_get_workspace_file_paths', return_value=["file1.txt", "file2.txt"])
    event_data = {"workspace_id": "1"}

    # Act
    deletion_worker._handle_workspace_deletion(event_data)

    # Assert
    deletion_worker.qdrant_client.delete_collection.assert_called_once_with("test_collection")
    assert deletion_worker.blob_storage.delete_file.call_count == 2
    deletion_worker.db_connection.get_cursor.assert_called_with() # Check that db was touched
    assert deletion_worker.publish_event.call_count == 2 # deleting and completed status

def test_handle_document_deletion(deletion_worker: DeletionWorker, mocker):
    """
    Test that the deletion worker handles a document deletion event successfully.
    """
    # Arrange
    mocker.patch.object(deletion_worker, '_get_workspace_collection', return_value="test_collection")
    mocker.patch.object(deletion_worker, '_get_document_chunk_ids', return_value=["chunk1", "chunk2"])
    event_data = {
        "document_id": "1",
        "workspace_id": "1",
        "file_path": "file1.txt"
    }

    # Act
    deletion_worker._handle_document_deletion(event_data)

    # Assert
    deletion_worker.qdrant_client.delete_points.assert_called_once_with(
        collection_name="test_collection",
        points_selector=["chunk1", "chunk2"]
    )
    deletion_worker.blob_storage.delete_file.assert_called_once_with("file1.txt")
