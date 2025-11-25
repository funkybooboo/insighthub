"""
Unit tests for storage implementations.

These tests verify the BlobStorage interface implementations correctly
handle file upload, download, delete, and hash operations.
"""

import io

from shared.storage.blob_storage import BlobStorage, BlobStorageError
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage


class TestBlobStorageError:
    """Test BlobStorageError class input/output."""

    def test_creation_with_message(self) -> None:
        """BlobStorageError stores message."""
        error = BlobStorageError("File not found")

        assert error.message == "File not found"

    def test_default_code(self) -> None:
        """BlobStorageError has default code STORAGE_ERROR."""
        error = BlobStorageError("Error")

        assert error.code == "STORAGE_ERROR"

    def test_custom_code(self) -> None:
        """BlobStorageError accepts custom code."""
        error = BlobStorageError("Not found", code="NOT_FOUND")

        assert error.code == "NOT_FOUND"

    def test_str_format(self) -> None:
        """BlobStorageError str() returns formatted message."""
        error = BlobStorageError("Upload failed", code="UPLOAD_ERROR")

        result = str(error)

        assert result == "[UPLOAD_ERROR] Upload failed"

    def test_str_with_default_code(self) -> None:
        """BlobStorageError str() with default code."""
        error = BlobStorageError("Something went wrong")

        result = str(error)

        assert result == "[STORAGE_ERROR] Something went wrong"


class TestInMemoryBlobStorageUpload:
    """Test InMemoryBlobStorage upload operations."""

    def test_upload_file_returns_ok(self) -> None:
        """upload_file returns Ok with object name."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"file content")

        result = storage.upload_file(file_obj, "test.txt")

        assert result.is_ok()
        assert result.unwrap() == "test.txt"

    def test_upload_file_stores_content(self) -> None:
        """upload_file stores file content."""
        storage = InMemoryBlobStorage()
        content = b"test file content"
        file_obj = io.BytesIO(content)

        storage.upload_file(file_obj, "test.txt")

        # Verify by downloading
        download_result = storage.download_file("test.txt")
        assert download_result.is_ok()
        assert download_result.unwrap() == content

    def test_upload_file_overwrites_existing(self) -> None:
        """upload_file overwrites existing file."""
        storage = InMemoryBlobStorage()

        storage.upload_file(io.BytesIO(b"original"), "test.txt")
        storage.upload_file(io.BytesIO(b"updated"), "test.txt")

        result = storage.download_file("test.txt")
        assert result.unwrap() == b"updated"

    def test_upload_empty_file(self) -> None:
        """upload_file handles empty files."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"")

        result = storage.upload_file(file_obj, "empty.txt")

        assert result.is_ok()
        download_result = storage.download_file("empty.txt")
        assert download_result.unwrap() == b""

    def test_upload_binary_content(self) -> None:
        """upload_file handles binary content."""
        storage = InMemoryBlobStorage()
        # Binary PDF header
        content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3"
        file_obj = io.BytesIO(content)

        result = storage.upload_file(file_obj, "document.pdf")

        assert result.is_ok()
        assert storage.download_file("document.pdf").unwrap() == content

    def test_upload_large_file(self) -> None:
        """upload_file handles large files."""
        storage = InMemoryBlobStorage()
        # 1MB of data
        content = b"x" * (1024 * 1024)
        file_obj = io.BytesIO(content)

        result = storage.upload_file(file_obj, "large.bin")

        assert result.is_ok()
        assert len(storage.download_file("large.bin").unwrap()) == 1024 * 1024

    def test_upload_with_nested_path(self) -> None:
        """upload_file handles nested object names."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"content")

        result = storage.upload_file(file_obj, "folder/subfolder/file.txt")

        assert result.is_ok()
        assert result.unwrap() == "folder/subfolder/file.txt"
        assert storage.file_exists("folder/subfolder/file.txt")


class TestInMemoryBlobStorageDownload:
    """Test InMemoryBlobStorage download operations."""

    def test_download_existing_file(self) -> None:
        """download_file returns Ok with content for existing file."""
        storage = InMemoryBlobStorage()
        content = b"download test content"
        storage.upload_file(io.BytesIO(content), "test.txt")

        result = storage.download_file("test.txt")

        assert result.is_ok()
        assert result.unwrap() == content

    def test_download_nonexistent_file(self) -> None:
        """download_file returns Err for nonexistent file."""
        storage = InMemoryBlobStorage()

        result = storage.download_file("nonexistent.txt")

        assert result.is_err()
        error = result.err()
        assert error.code == "NOT_FOUND"
        assert "nonexistent.txt" in error.message

    def test_download_preserves_binary_data(self) -> None:
        """download_file preserves exact binary content."""
        storage = InMemoryBlobStorage()
        # Binary data with various byte values
        content = bytes(range(256))
        storage.upload_file(io.BytesIO(content), "binary.bin")

        result = storage.download_file("binary.bin")

        assert result.unwrap() == content


class TestInMemoryBlobStorageDelete:
    """Test InMemoryBlobStorage delete operations."""

    def test_delete_existing_file_returns_true(self) -> None:
        """delete_file returns Ok(True) for existing file."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content"), "test.txt")

        result = storage.delete_file("test.txt")

        assert result.is_ok()
        assert result.unwrap() is True

    def test_delete_removes_file(self) -> None:
        """delete_file removes the file from storage."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content"), "test.txt")

        storage.delete_file("test.txt")

        assert storage.file_exists("test.txt") is False

    def test_delete_nonexistent_file_returns_false(self) -> None:
        """delete_file returns Ok(False) for nonexistent file."""
        storage = InMemoryBlobStorage()

        result = storage.delete_file("nonexistent.txt")

        assert result.is_ok()
        assert result.unwrap() is False

    def test_delete_one_of_multiple_files(self) -> None:
        """delete_file only removes specified file."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content1"), "file1.txt")
        storage.upload_file(io.BytesIO(b"content2"), "file2.txt")
        storage.upload_file(io.BytesIO(b"content3"), "file3.txt")

        storage.delete_file("file2.txt")

        assert storage.file_exists("file1.txt") is True
        assert storage.file_exists("file2.txt") is False
        assert storage.file_exists("file3.txt") is True


class TestInMemoryBlobStorageExists:
    """Test InMemoryBlobStorage file existence checks."""

    def test_file_exists_returns_true_for_existing(self) -> None:
        """file_exists returns True for existing file."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content"), "test.txt")

        result = storage.file_exists("test.txt")

        assert result is True

    def test_file_exists_returns_false_for_nonexistent(self) -> None:
        """file_exists returns False for nonexistent file."""
        storage = InMemoryBlobStorage()

        result = storage.file_exists("nonexistent.txt")

        assert result is False

    def test_file_exists_after_delete(self) -> None:
        """file_exists returns False after file is deleted."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content"), "test.txt")
        storage.delete_file("test.txt")

        result = storage.file_exists("test.txt")

        assert result is False

    def test_file_exists_with_nested_path(self) -> None:
        """file_exists works with nested paths."""
        storage = InMemoryBlobStorage()
        storage.upload_file(io.BytesIO(b"content"), "a/b/c/file.txt")

        assert storage.file_exists("a/b/c/file.txt") is True
        assert storage.file_exists("a/b/c/other.txt") is False


class TestInMemoryBlobStorageHash:
    """Test InMemoryBlobStorage hash calculation."""

    def test_calculate_hash_returns_sha256(self) -> None:
        """calculate_hash returns SHA-256 hex digest."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"test content")

        result = storage.calculate_hash(file_obj)

        # SHA-256 is 64 hex characters
        assert len(result) == 64
        # Should be hex string
        assert all(c in "0123456789abcdef" for c in result)

    def test_calculate_hash_deterministic(self) -> None:
        """calculate_hash returns same hash for same content."""
        storage = InMemoryBlobStorage()
        content = b"same content"

        hash1 = storage.calculate_hash(io.BytesIO(content))
        hash2 = storage.calculate_hash(io.BytesIO(content))

        assert hash1 == hash2

    def test_calculate_hash_different_for_different_content(self) -> None:
        """calculate_hash returns different hashes for different content."""
        storage = InMemoryBlobStorage()

        hash1 = storage.calculate_hash(io.BytesIO(b"content A"))
        hash2 = storage.calculate_hash(io.BytesIO(b"content B"))

        assert hash1 != hash2

    def test_calculate_hash_known_value(self) -> None:
        """calculate_hash returns correct known SHA-256 value."""
        storage = InMemoryBlobStorage()
        # SHA-256 of "hello world" (without newline)
        file_obj = io.BytesIO(b"hello world")

        result = storage.calculate_hash(file_obj)

        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        assert result == expected

    def test_calculate_hash_empty_file(self) -> None:
        """calculate_hash handles empty files."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"")

        result = storage.calculate_hash(file_obj)

        # SHA-256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_calculate_hash_preserves_file_position(self) -> None:
        """calculate_hash resets file position after hashing."""
        storage = InMemoryBlobStorage()
        file_obj = io.BytesIO(b"test content")
        file_obj.seek(5)  # Start at offset

        storage.calculate_hash(file_obj)

        # Position should be reset to 0
        assert file_obj.tell() == 0

    def test_calculate_hash_large_file(self) -> None:
        """calculate_hash handles large files in chunks."""
        storage = InMemoryBlobStorage()
        # 10MB of data
        content = b"x" * (10 * 1024 * 1024)
        file_obj = io.BytesIO(content)

        result = storage.calculate_hash(file_obj)

        # Should complete without error and return valid hash
        assert len(result) == 64


class TestInMemoryBlobStorageInterface:
    """Test InMemoryBlobStorage implements BlobStorage interface."""

    def test_is_instance_of_blob_storage(self) -> None:
        """InMemoryBlobStorage is instance of BlobStorage."""
        storage = InMemoryBlobStorage()

        assert isinstance(storage, BlobStorage)

    def test_has_all_interface_methods(self) -> None:
        """InMemoryBlobStorage has all required interface methods."""
        storage = InMemoryBlobStorage()

        assert hasattr(storage, "upload_file")
        assert hasattr(storage, "download_file")
        assert hasattr(storage, "delete_file")
        assert hasattr(storage, "file_exists")
        assert hasattr(storage, "calculate_hash")

        assert callable(storage.upload_file)
        assert callable(storage.download_file)
        assert callable(storage.delete_file)
        assert callable(storage.file_exists)
        assert callable(storage.calculate_hash)


class TestInMemoryBlobStorageIsolation:
    """Test InMemoryBlobStorage instance isolation."""

    def test_instances_are_isolated(self) -> None:
        """Separate instances have isolated storage."""
        storage1 = InMemoryBlobStorage()
        storage2 = InMemoryBlobStorage()

        storage1.upload_file(io.BytesIO(b"content1"), "file.txt")

        assert storage1.file_exists("file.txt") is True
        assert storage2.file_exists("file.txt") is False

    def test_fresh_instance_is_empty(self) -> None:
        """New instance has no stored files."""
        storage = InMemoryBlobStorage()

        assert storage.file_exists("any_file.txt") is False
