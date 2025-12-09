import os
import shutil
import tempfile

import pytest
from returns.result import Failure, Success

from src.infrastructure.storage.file_system_storage import FileSystemBlobStorage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


class TestFileSystemStorageIntegration:
    def test_fs_connection(self, temp_dir):
        """Test that the FileSystemStorage can be initialized."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        assert isinstance(storage, FileSystemBlobStorage)

    def test_upload_and_download(self, temp_dir):
        """Test uploading and downloading a file."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        file_content = b"test content"
        object_name = "test_file.txt"

        # Upload
        upload_result = storage.upload(object_name, file_content)
        assert isinstance(upload_result, Success)

        # Download
        download_result = storage.download(object_name)
        assert isinstance(download_result, Success)
        assert download_result.unwrap() == file_content

    def test_download_nonexistent_object(self, temp_dir):
        """Test downloading a non-existent object."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        object_name = "nonexistent_file.txt"

        download_result = storage.download(object_name)
        assert isinstance(download_result, Failure)

    def test_delete(self, temp_dir):
        """Test deleting an object."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        file_content = b"delete me"
        object_name = "delete_me.txt"

        storage.upload(object_name, file_content)

        # Delete
        delete_result = storage.delete(object_name)
        assert delete_result is True

        # Verify deletion
        download_result = storage.download(object_name)
        assert isinstance(download_result, Failure)

    def test_exists(self, temp_dir):
        """Test the exists method."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        object_name = "existing_file.txt"

        assert not storage.exists(object_name)

        storage.upload(object_name, b"exists")

        assert storage.exists(object_name)

    def test_get_url(self, temp_dir):
        """Test getting a URL for an object."""
        storage = FileSystemBlobStorage(base_path=temp_dir)
        object_name = "url_test.txt"
        storage.upload(object_name, b"url")

        url_result = storage.get_url(object_name)
        assert isinstance(url_result, Success)
        expected_path = os.path.join(temp_dir, object_name)
        assert url_result.unwrap() == f"file://{expected_path}"
