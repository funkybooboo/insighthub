"""Unit tests for blob storage implementations."""

import io
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from src.infrastructure.storage.file_system_blob_storage import FileSystemBlobStorage
from src.infrastructure.storage.in_memory_blob_storage import InMemoryBlobStorage


class TestInMemoryBlobStorage:
    """Tests for in-memory blob storage."""

    @pytest.fixture
    def storage(self) -> InMemoryBlobStorage:
        """Provide a fresh storage instance."""
        return InMemoryBlobStorage()

    def test_initialization(self, storage: InMemoryBlobStorage) -> None:
        """Test storage initialization."""
        assert isinstance(storage.storage, dict)
        assert len(storage.storage) == 0

    def test_upload_file(self, storage: InMemoryBlobStorage) -> None:
        """Test uploading a file."""
        content = b"test content"
        file_obj = io.BytesIO(content)

        result = storage.upload_file(file_obj, "test.txt")

        assert result == "test.txt"
        assert "test.txt" in storage.storage
        assert storage.storage["test.txt"] == content

    def test_upload_multiple_files(self, storage: InMemoryBlobStorage) -> None:
        """Test uploading multiple files."""
        files = {
            "file1.txt": b"content1",
            "file2.txt": b"content2",
            "file3.txt": b"content3",
        }

        for name, content in files.items():
            file_obj = io.BytesIO(content)
            storage.upload_file(file_obj, name)

        assert len(storage.storage) == 3
        for name, content in files.items():
            assert storage.storage[name] == content

    def test_download_file_success(self, storage: InMemoryBlobStorage) -> None:
        """Test downloading an existing file."""
        content = b"test content"
        file_obj = io.BytesIO(content)
        storage.upload_file(file_obj, "test.txt")

        downloaded = storage.download_file("test.txt")

        assert downloaded == content

    def test_download_file_not_found(self, storage: InMemoryBlobStorage) -> None:
        """Test downloading a non-existent file."""
        with pytest.raises(Exception, match="File not found"):
            storage.download_file("nonexistent.txt")

    def test_delete_file_success(self, storage: InMemoryBlobStorage) -> None:
        """Test deleting an existing file."""
        file_obj = io.BytesIO(b"content")
        storage.upload_file(file_obj, "test.txt")

        result = storage.delete_file("test.txt")

        assert result is True
        assert "test.txt" not in storage.storage

    def test_delete_file_not_found(self, storage: InMemoryBlobStorage) -> None:
        """Test deleting a non-existent file."""
        result = storage.delete_file("nonexistent.txt")
        assert result is False

    def test_file_exists_true(self, storage: InMemoryBlobStorage) -> None:
        """Test checking if file exists when it does."""
        file_obj = io.BytesIO(b"content")
        storage.upload_file(file_obj, "test.txt")

        assert storage.file_exists("test.txt") is True

    def test_file_exists_false(self, storage: InMemoryBlobStorage) -> None:
        """Test checking if file exists when it doesn't."""
        assert storage.file_exists("nonexistent.txt") is False

    def test_calculate_hash_consistent(self, storage: InMemoryBlobStorage) -> None:
        """Test that hash calculation is consistent."""
        content = b"test content"
        file_obj1 = io.BytesIO(content)
        file_obj2 = io.BytesIO(content)

        hash1 = storage.calculate_hash(file_obj1)
        hash2 = storage.calculate_hash(file_obj2)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_calculate_hash_different_content(self, storage: InMemoryBlobStorage) -> None:
        """Test that different content produces different hashes."""
        file_obj1 = io.BytesIO(b"content1")
        file_obj2 = io.BytesIO(b"content2")

        hash1 = storage.calculate_hash(file_obj1)
        hash2 = storage.calculate_hash(file_obj2)

        assert hash1 != hash2

    def test_upload_resets_file_position(self, storage: InMemoryBlobStorage) -> None:
        """Test that upload resets file position."""
        content = b"test content"
        file_obj = io.BytesIO(content)
        file_obj.seek(5)

        storage.upload_file(file_obj, "test.txt")

        assert storage.storage["test.txt"] == content

    def test_calculate_hash_resets_position(self, storage: InMemoryBlobStorage) -> None:
        """Test that hash calculation resets file position."""
        content = b"test content"
        file_obj = io.BytesIO(content)

        storage.calculate_hash(file_obj)

        assert file_obj.tell() == 0

    def test_upload_overwrite_existing(self, storage: InMemoryBlobStorage) -> None:
        """Test that uploading overwrites existing files."""
        file_obj1 = io.BytesIO(b"old content")
        storage.upload_file(file_obj1, "test.txt")

        file_obj2 = io.BytesIO(b"new content")
        storage.upload_file(file_obj2, "test.txt")

        assert storage.storage["test.txt"] == b"new content"

    def test_binary_content_preserved(self, storage: InMemoryBlobStorage) -> None:
        """Test that binary content is preserved correctly."""
        binary_content = bytes(range(256))
        file_obj = io.BytesIO(binary_content)

        storage.upload_file(file_obj, "binary.dat")
        downloaded = storage.download_file("binary.dat")

        assert downloaded == binary_content


class TestFileSystemBlobStorage:
    """Tests for file system blob storage."""

    @pytest.fixture
    def temp_dir(self) -> Iterator[str]:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage(self, temp_dir: str) -> FileSystemBlobStorage:
        """Provide a fresh storage instance."""
        return FileSystemBlobStorage(temp_dir)

    def test_initialization_creates_directory(self, temp_dir: str) -> None:
        """Test that initialization creates base directory."""
        base_path = os.path.join(temp_dir, "new_storage")
        storage = FileSystemBlobStorage(base_path)

        assert os.path.exists(base_path)
        assert storage.base_path == Path(base_path)

    def test_initialization_existing_directory(self, temp_dir: str) -> None:
        """Test initialization with existing directory."""
        storage = FileSystemBlobStorage(temp_dir)
        assert storage.base_path == Path(temp_dir)

    def test_upload_file(self, storage: FileSystemBlobStorage, temp_dir: str) -> None:
        """Test uploading a file."""
        content = b"test content"
        file_obj = io.BytesIO(content)

        result = storage.upload_file(file_obj, "test.txt")

        assert result == "test.txt"
        file_path = Path(temp_dir) / "test.txt"
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_upload_file_with_nested_path(
        self, storage: FileSystemBlobStorage, temp_dir: str
    ) -> None:
        """Test uploading file with nested directory structure."""
        content = b"test content"
        file_obj = io.BytesIO(content)

        result = storage.upload_file(file_obj, "folder/subfolder/test.txt")

        assert result == "folder/subfolder/test.txt"
        file_path = Path(temp_dir) / "folder" / "subfolder" / "test.txt"
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_download_file_success(self, storage: FileSystemBlobStorage) -> None:
        """Test downloading an existing file."""
        content = b"test content"
        file_obj = io.BytesIO(content)
        storage.upload_file(file_obj, "test.txt")

        downloaded = storage.download_file("test.txt")

        assert downloaded == content

    def test_download_file_not_found(self, storage: FileSystemBlobStorage) -> None:
        """Test downloading a non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            storage.download_file("nonexistent.txt")

    def test_delete_file_success(self, storage: FileSystemBlobStorage, temp_dir: str) -> None:
        """Test deleting an existing file."""
        file_obj = io.BytesIO(b"content")
        storage.upload_file(file_obj, "test.txt")

        result = storage.delete_file("test.txt")

        assert result is True
        file_path = Path(temp_dir) / "test.txt"
        assert not file_path.exists()

    def test_delete_file_not_found(self, storage: FileSystemBlobStorage) -> None:
        """Test deleting a non-existent file."""
        result = storage.delete_file("nonexistent.txt")
        assert result is False

    def test_delete_file_cleans_empty_directories(
        self, storage: FileSystemBlobStorage, temp_dir: str
    ) -> None:
        """Test that delete cleans up empty parent directories."""
        file_obj = io.BytesIO(b"content")
        storage.upload_file(file_obj, "folder/subfolder/test.txt")

        storage.delete_file("folder/subfolder/test.txt")

        folder_path = Path(temp_dir) / "folder"
        assert not folder_path.exists()

    def test_delete_file_keeps_non_empty_directories(
        self, storage: FileSystemBlobStorage, temp_dir: str
    ) -> None:
        """Test that delete keeps non-empty directories."""
        file_obj1 = io.BytesIO(b"content1")
        file_obj2 = io.BytesIO(b"content2")
        storage.upload_file(file_obj1, "folder/file1.txt")
        storage.upload_file(file_obj2, "folder/file2.txt")

        storage.delete_file("folder/file1.txt")

        folder_path = Path(temp_dir) / "folder"
        assert folder_path.exists()
        assert (folder_path / "file2.txt").exists()

    def test_file_exists_true(self, storage: FileSystemBlobStorage) -> None:
        """Test checking if file exists when it does."""
        file_obj = io.BytesIO(b"content")
        storage.upload_file(file_obj, "test.txt")

        assert storage.file_exists("test.txt") is True

    def test_file_exists_false(self, storage: FileSystemBlobStorage) -> None:
        """Test checking if file exists when it doesn't."""
        assert storage.file_exists("nonexistent.txt") is False

    def test_calculate_hash_consistent(self, storage: FileSystemBlobStorage) -> None:
        """Test that hash calculation is consistent."""
        content = b"test content"
        file_obj1 = io.BytesIO(content)
        file_obj2 = io.BytesIO(content)

        hash1 = storage.calculate_hash(file_obj1)
        hash2 = storage.calculate_hash(file_obj2)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_calculate_hash_different_content(self, storage: FileSystemBlobStorage) -> None:
        """Test that different content produces different hashes."""
        file_obj1 = io.BytesIO(b"content1")
        file_obj2 = io.BytesIO(b"content2")

        hash1 = storage.calculate_hash(file_obj1)
        hash2 = storage.calculate_hash(file_obj2)

        assert hash1 != hash2

    def test_upload_overwrite_existing(self, storage: FileSystemBlobStorage) -> None:
        """Test that uploading overwrites existing files."""
        file_obj1 = io.BytesIO(b"old content")
        storage.upload_file(file_obj1, "test.txt")

        file_obj2 = io.BytesIO(b"new content")
        storage.upload_file(file_obj2, "test.txt")

        downloaded = storage.download_file("test.txt")
        assert downloaded == b"new content"

    def test_binary_content_preserved(self, storage: FileSystemBlobStorage) -> None:
        """Test that binary content is preserved correctly."""
        binary_content = bytes(range(256))
        file_obj = io.BytesIO(binary_content)

        storage.upload_file(file_obj, "binary.dat")
        downloaded = storage.download_file("binary.dat")

        assert downloaded == binary_content

    def test_large_file_upload(self, storage: FileSystemBlobStorage) -> None:
        """Test uploading a large file."""
        large_content = b"x" * (10 * 1024 * 1024)
        file_obj = io.BytesIO(large_content)

        storage.upload_file(file_obj, "large.dat")
        downloaded = storage.download_file("large.dat")

        assert downloaded == large_content

    def test_get_full_path(self, storage: FileSystemBlobStorage, temp_dir: str) -> None:
        """Test _get_full_path helper method."""
        full_path = storage._get_full_path("folder/file.txt")

        expected_path = Path(temp_dir) / "folder" / "file.txt"
        assert full_path == expected_path
        assert full_path.parent.exists()
