"""Integration tests for blob storage functionality."""

import hashlib
import io
from typing import BinaryIO

import pytest

from shared.storage.blob_storage import BlobStorage, BlobStorageError
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage
from shared.storage.result import Ok, Err, Result


class FakeBlobStorage(BlobStorage):
    """Fake blob storage for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.storage: dict[str, bytes] = {}

    def upload_file(self, file_obj: BinaryIO, blob_key: str) -> Result[str, BlobStorageError]:
        """Upload a file to in-memory storage."""
        file_obj.seek(0)
        self.storage[blob_key] = file_obj.read()
        return Ok(blob_key)

    def download_file(self, blob_key: str) -> Result[bytes, BlobStorageError]:
        """Download a file from in-memory storage."""
        if blob_key not in self.storage:
            return Err(BlobStorageError(f"Blob not found: {blob_key}"))
        return Ok(self.storage[blob_key])

    def delete_file(self, blob_key: str) -> Result[bool, BlobStorageError]:
        """Delete a file from in-memory storage."""
        if blob_key in self.storage:
            del self.storage[blob_key]
            return Ok(True)
        return Ok(False)

    def file_exists(self, blob_key: str) -> bool:
        """Check if file exists."""
        return blob_key in self.storage

    def list_files(self, prefix: str | None = None) -> list[str]:
        """List all files with optional prefix filter."""
        if prefix:
            return [key for key in self.storage if key.startswith(prefix)]
        return list(self.storage.keys())

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """Calculate hash of file."""
        file_obj.seek(0)
        content = file_obj.read()
        file_obj.seek(0)
        return hashlib.sha256(content).hexdigest()


class TestBlobStorageInterface:
    """Test blob storage interface compliance."""

    @pytest.fixture
    def blob_storage(self) -> BlobStorage:
        """Get blob storage instance for testing."""
        return InMemoryBlobStorage()

    def test_upload_file_success(self, blob_storage: BlobStorage) -> None:
        """Test successful file upload."""
        content = b"Test file content"
        file_obj = io.BytesIO(content)
        blob_key = "test/file.txt"

        result = blob_storage.upload_file(file_obj, blob_key)

        assert result.is_ok()
        assert result.unwrap() == blob_key

    def test_download_file_success(self, blob_storage: BlobStorage) -> None:
        """Test successful file download."""
        content = b"Test file content"
        file_obj = io.BytesIO(content)
        blob_key = "test/file.txt"

        # Upload first
        upload_result = blob_storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # Then download
        download_result = blob_storage.download_file(blob_key)
        assert download_result.is_ok()
        assert download_result.unwrap() == content

    def test_download_file_not_found(self, blob_storage: BlobStorage) -> None:
        """Test downloading non-existent file."""
        blob_key = "nonexistent/file.txt"

        result = blob_storage.download_file(blob_key)
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, BlobStorageError)
        assert "not found" in str(error).lower()

    def test_delete_file_success(self, blob_storage: BlobStorage) -> None:
        """Test successful file deletion."""
        content = b"Test file content"
        file_obj = io.BytesIO(content)
        blob_key = "test/file.txt"

        # Upload first
        upload_result = blob_storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # Verify it exists
        assert blob_storage.file_exists(blob_key)

        # Delete
        delete_result = blob_storage.delete_file(blob_key)
        assert delete_result.is_ok()
        assert delete_result.unwrap() is True

        # Verify it's gone
        assert not blob_storage.file_exists(blob_key)

    def test_delete_file_not_found(self, blob_storage: BlobStorage) -> None:
        """Test deleting non-existent file."""
        blob_key = "nonexistent/file.txt"

        result = blob_storage.delete_file(blob_key)
        assert result.is_ok()
        assert result.unwrap() is False

    def test_file_exists(self, blob_storage: BlobStorage) -> None:
        """Test file existence checking."""
        content = b"Test file content"
        file_obj = io.BytesIO(content)
        blob_key = "test/file.txt"

        # File doesn't exist initially
        assert not blob_storage.file_exists(blob_key)

        # Upload file
        upload_result = blob_storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # File exists now
        assert blob_storage.file_exists(blob_key)

    def test_list_files_empty(self, blob_storage: BlobStorage) -> None:
        """Test listing files when storage is empty."""
        files = blob_storage.list_files()
        assert files == []

    def test_list_files_with_content(self, blob_storage: BlobStorage) -> None:
        """Test listing files with content."""
        # Upload some files
        files_to_upload = [
            ("test/file1.txt", b"content1"),
            ("test/file2.txt", b"content2"),
            ("other/file3.txt", b"content3"),
        ]

        for blob_key, content in files_to_upload:
            file_obj = io.BytesIO(content)
            result = blob_storage.upload_file(file_obj, blob_key)
            assert result.is_ok()

        # List all files
        all_files = blob_storage.list_files()
        assert len(all_files) == 3
        assert "test/file1.txt" in all_files
        assert "test/file2.txt" in all_files
        assert "other/file3.txt" in all_files

        # List files with prefix
        test_files = blob_storage.list_files("test/")
        assert len(test_files) == 2
        assert "test/file1.txt" in test_files
        assert "test/file2.txt" in test_files

        # List files with other prefix
        other_files = blob_storage.list_files("other/")
        assert len(other_files) == 1
        assert "other/file3.txt" in other_files


class TestInMemoryBlobStorage:
    """Test InMemoryBlobStorage implementation."""

    @pytest.fixture
    def storage(self) -> InMemoryBlobStorage:
        """Get InMemoryBlobStorage instance."""
        return InMemoryBlobStorage()

    def test_calculate_hash(self, storage: InMemoryBlobStorage) -> None:
        """Test hash calculation."""
        content = b"Test content for hashing"
        file_obj = io.BytesIO(content)

        # Calculate expected hash
        expected_hash = hashlib.sha256(content).hexdigest()

        # Calculate using storage
        actual_hash = storage.calculate_hash(file_obj)

        assert actual_hash == expected_hash

    def test_calculate_hash_resets_position(self, storage: InMemoryBlobStorage) -> None:
        """Test that calculate_hash resets file position."""
        content = b"Test content"
        file_obj = io.BytesIO(content)

        # Move position to middle
        file_obj.seek(5)

        # Calculate hash
        storage.calculate_hash(file_obj)

        # Position should be reset to beginning
        assert file_obj.tell() == 0

    def test_upload_file_preserves_content(self, storage: InMemoryBlobStorage) -> None:
        """Test that upload preserves file content exactly."""
        original_content = b"This is some test content with special chars: \x00\x01\x02"
        file_obj = io.BytesIO(original_content)
        blob_key = "test/file.bin"

        # Upload
        upload_result = storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # Download and verify
        download_result = storage.download_file(blob_key)
        assert download_result.is_ok()
        retrieved_content = download_result.unwrap()

        assert retrieved_content == original_content

    def test_upload_file_handles_large_content(self, storage: InMemoryBlobStorage) -> None:
        """Test uploading and retrieving large files."""
        # Create 1MB of content
        large_content = b"A" * (1024 * 1024)
        file_obj = io.BytesIO(large_content)
        blob_key = "test/large_file.dat"

        # Upload
        upload_result = storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # Download and verify
        download_result = storage.download_file(blob_key)
        assert download_result.is_ok()
        retrieved_content = download_result.unwrap()

        assert retrieved_content == large_content
        assert len(retrieved_content) == 1024 * 1024

    def test_concurrent_operations(self, storage: InMemoryBlobStorage) -> None:
        """Test that storage handles concurrent operations correctly."""
        import threading
        import time

        results = []
        errors = []

        def upload_worker(worker_id: int) -> None:
            try:
                content = f"Content from worker {worker_id}".encode()
                file_obj = io.BytesIO(content)
                blob_key = f"test/worker_{worker_id}.txt"

                result = storage.upload_file(file_obj, blob_key)
                results.append((worker_id, result.is_ok()))

                # Small delay to increase chance of race conditions
                time.sleep(0.001)

                # Verify we can read it back
                download_result = storage.download_file(blob_key)
                if download_result.is_ok():
                    retrieved = download_result.unwrap()
                    assert retrieved == content
                else:
                    errors.append(f"Download failed for worker {worker_id}")

            except Exception as e:
                errors.append(f"Worker {worker_id} error: {e}")

        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=upload_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all uploads succeeded
        assert len(results) == 10
        assert all(success for _, success in results)
        assert len(errors) == 0

        # Verify all files exist
        all_files = storage.list_files("test/")
        assert len(all_files) == 10
        for i in range(10):
            assert f"test/worker_{i}.txt" in all_files


class TestBlobStorageIntegration:
    """Integration tests combining blob storage with document operations."""

    def test_document_upload_integration(self, blob_storage: BlobStorage) -> None:
        """Test document upload workflow with blob storage."""
        # This would typically be an integration test that combines
        # document service with blob storage

        # Upload a document
        content = b"This is a test document content."
        file_obj = io.BytesIO(content)
        blob_key = "documents/test.txt"

        upload_result = blob_storage.upload_file(file_obj, blob_key)
        assert upload_result.is_ok()

        # Verify it can be retrieved
        download_result = blob_storage.download_file(blob_key)
        assert download_result.is_ok()
        assert download_result.unwrap() == content

        # Verify it exists in listings
        files = blob_storage.list_files("documents/")
        assert blob_key in files

        # Clean up
        delete_result = blob_storage.delete_file(blob_key)
        assert delete_result.is_ok()
        assert not blob_storage.file_exists(blob_key)


class TestDocumentServiceBlobStorageIntegration:
    """Test document service integration with blob storage."""

    @pytest.fixture
    def fake_storage(self) -> FakeBlobStorage:
        """Provide a fake blob storage."""
        return FakeBlobStorage()

    def test_upload_stores_in_blob_storage(self, fake_storage: FakeBlobStorage) -> None:
        """Test that document upload stores file in blob storage."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        # Simulate what document service does
        blob_key = "test/document.txt"
        result = fake_storage.upload_file(file_obj, blob_key)

        assert result.is_ok()
        assert result.unwrap() == blob_key
        assert len(fake_storage.storage) == 1
        assert fake_storage.storage[blob_key] == content