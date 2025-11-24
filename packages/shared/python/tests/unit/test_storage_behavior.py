"""
Behavior tests for blob storage implementations.

These tests verify WHAT storage does (inputs/outputs),
not HOW it does it (implementation details).
"""

from io import BytesIO
from typing import Optional

from shared.storage import BlobStorageType, InMemoryBlobStorage, create_blob_storage


class TestInMemoryStorageBehavior:
    """Test InMemoryBlobStorage input/output behavior."""

    def test_upload_and_download_returns_same_content(self) -> None:
        """Given content, when uploaded and downloaded, returns identical bytes."""
        storage = InMemoryBlobStorage()
        content = b"Hello, World!"

        # Upload content
        storage.upload_file(BytesIO(content), "test.txt")

        # Download should return same content
        downloaded = storage.download_file("test.txt")
        assert downloaded.is_ok()
        assert downloaded.unwrap() == content

    def test_file_exists_returns_true_after_upload(self) -> None:
        """Given uploaded content, file_exists returns True."""
        storage = InMemoryBlobStorage()
        storage.upload_file(BytesIO(b"content"), "file.txt")

        assert storage.file_exists("file.txt") is True

    def test_file_exists_returns_false_for_nonexistent(self) -> None:
        """Given nonexistent key, file_exists returns False."""
        storage = InMemoryBlobStorage()

        assert storage.file_exists("missing.txt") is False

    def test_delete_removes_content(self) -> None:
        """Given uploaded content, delete_file removes it."""
        storage = InMemoryBlobStorage()
        storage.upload_file(BytesIO(b"delete me"), "to-delete.txt")

        # Verify exists
        assert storage.file_exists("to-delete.txt") is True

        # Delete
        result = storage.delete_file("to-delete.txt")

        # Verify gone
        assert result.is_ok()
        assert result.unwrap() is True
        assert storage.file_exists("to-delete.txt") is False

    def test_upload_overwrites_existing(self) -> None:
        """Uploading with same key overwrites existing content."""
        storage = InMemoryBlobStorage()

        storage.upload_file(BytesIO(b"original"), "file.txt")
        storage.upload_file(BytesIO(b"updated"), "file.txt")

        downloaded = storage.download_file("file.txt")
        assert downloaded.is_ok()
        assert downloaded.unwrap() == b"updated"

    def test_upload_returns_object_name(self) -> None:
        """Upload returns the object name/key."""
        storage = InMemoryBlobStorage()

        result = storage.upload_file(BytesIO(b"content"), "my-file.txt")

        assert result.is_ok()
        assert result.unwrap() == "my-file.txt"

    def test_calculate_hash_returns_consistent_hash(self) -> None:
        """Calculate hash returns same hash for same content."""
        storage = InMemoryBlobStorage()
        content = b"Hello, World!"

        hash1 = storage.calculate_hash(BytesIO(content))
        hash2 = storage.calculate_hash(BytesIO(content))

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex digest length


class TestBlobStorageFactoryBehavior:
    """Test storage factory input/output behavior."""

    def test_create_in_memory_returns_in_memory_storage(self) -> None:
        """Given 'in_memory' type, returns InMemoryBlobStorage."""
        result = create_blob_storage("in_memory")

        assert result is not None
        assert isinstance(result, InMemoryBlobStorage)

    def test_create_with_enum_works(self) -> None:
        """Factory accepts BlobStorageType enum values."""
        result = create_blob_storage(BlobStorageType.IN_MEMORY.value)

        assert result is not None
        assert isinstance(result, InMemoryBlobStorage)

    def test_create_file_system_requires_base_path(self) -> None:
        """File system storage requires base_path parameter."""
        result = create_blob_storage("file_system")

        assert result is None

    def test_create_s3_requires_credentials(self) -> None:
        """S3 storage requires all credentials."""
        result = create_blob_storage("s3")

        assert result is None

    def test_create_invalid_type_returns_nothing(self) -> None:
        """Invalid storage type returns None."""
        result = create_blob_storage("invalid_type")

        assert result is None


class TestBlobStorageTypeEnum:
    """Test BlobStorageType enum values."""

    def test_enum_has_expected_values(self) -> None:
        """Enum contains expected storage types."""
        assert BlobStorageType.S3.value == "s3"
        assert BlobStorageType.FILE_SYSTEM.value == "file_system"
        assert BlobStorageType.IN_MEMORY.value == "in_memory"
