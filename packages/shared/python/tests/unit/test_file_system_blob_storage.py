"""Unit tests for file system blob storage."""

import io
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from shared.storage.blob_storage import BlobStorageError
from shared.storage.file_system_blob_storage import FileSystemBlobStorage


class TestFileSystemBlobStorage:
    """Test FileSystemBlobStorage implementation."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def storage(self, temp_dir: Path) -> FileSystemBlobStorage:
        """Create a FileSystemBlobStorage instance."""
        return FileSystemBlobStorage(str(temp_dir))

    def test_initialization_creates_base_directory(self, temp_dir: Path) -> None:
        """Test that initialization creates the base directory if it doesn't exist."""
        sub_dir = temp_dir / "nested" / "storage"
        assert not sub_dir.exists()

        FileSystemBlobStorage(str(sub_dir))
        assert sub_dir.exists()
        assert sub_dir.is_dir()

    def test_upload_file_success(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test successful file upload."""
        content = b"Hello, World!"
        file_obj = io.BytesIO(content)
        object_name = "test.txt"

        result = storage.upload_file(file_obj, object_name)

        assert result.is_ok()
        assert result.unwrap() == object_name

        # Verify file was written
        file_path = temp_dir / object_name
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_upload_file_with_subdirectory(
        self, storage: FileSystemBlobStorage, temp_dir: Path
    ) -> None:
        """Test file upload creates subdirectories as needed."""
        content = b"Content"
        file_obj = io.BytesIO(content)
        object_name = "folder/subfolder/file.txt"

        result = storage.upload_file(file_obj, object_name)

        assert result.is_ok()
        assert result.unwrap() == object_name

        # Verify file and directories were created
        file_path = temp_dir / object_name
        assert file_path.exists()
        assert file_path.is_file()
        assert file_path.read_bytes() == content

        # Verify parent directories exist
        assert (temp_dir / "folder").exists()
        assert (temp_dir / "folder" / "subfolder").exists()

    def test_upload_file_os_error(self, storage: FileSystemBlobStorage) -> None:
        """Test upload file handles OS errors."""
        file_obj = io.BytesIO(b"content")
        object_name = "test.txt"

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            result = storage.upload_file(file_obj, object_name)

        assert result.is_err()
        error = result.err()
        assert isinstance(error, BlobStorageError)
        assert error.code == "UPLOAD_ERROR"
        assert "Upload failed" in error.message

    def test_download_file_success(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test successful file download."""
        content = b"File content"
        object_name = "download.txt"

        # Create file manually
        file_path = temp_dir / object_name
        file_path.write_bytes(content)

        result = storage.download_file(object_name)

        assert result.is_ok()
        assert result.unwrap() == content

    def test_download_file_not_found(self, storage: FileSystemBlobStorage) -> None:
        """Test download file when file doesn't exist."""
        result = storage.download_file("nonexistent.txt")

        assert result.is_err()
        error = result.err()
        assert isinstance(error, BlobStorageError)
        assert error.code == "NOT_FOUND"
        assert "File not found" in error.message

    def test_download_file_os_error(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test download file handles OS errors."""
        object_name = "error.txt"

        # Create file
        file_path = temp_dir / object_name
        file_path.write_bytes(b"content")

        with patch("builtins.open", side_effect=OSError("Read error")):
            result = storage.download_file(object_name)

        assert result.is_err()
        error = result.err()
        assert isinstance(error, BlobStorageError)
        assert error.code == "DOWNLOAD_ERROR"
        assert "Download failed" in error.message

    def test_delete_file_success(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test successful file deletion."""
        object_name = "delete.txt"

        # Create file
        file_path = temp_dir / object_name
        file_path.write_bytes(b"content")

        result = storage.delete_file(object_name)

        assert result.is_ok()
        assert result.unwrap() is True
        assert not file_path.exists()

    def test_delete_file_not_found(self, storage: FileSystemBlobStorage) -> None:
        """Test delete file when file doesn't exist."""
        result = storage.delete_file("nonexistent.txt")

        assert result.is_ok()
        assert result.unwrap() is False

    def test_delete_file_with_empty_directory_cleanup(
        self, storage: FileSystemBlobStorage, temp_dir: Path
    ) -> None:
        """Test that empty directories are cleaned up after file deletion."""
        object_name = "nested/deep/file.txt"

        # Create nested file
        file_path = temp_dir / object_name
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"content")

        # Verify directories exist
        assert (temp_dir / "nested").exists()
        assert (temp_dir / "nested" / "deep").exists()

        # Delete file
        result = storage.delete_file(object_name)

        assert result.is_ok()
        assert result.unwrap() is True
        assert not file_path.exists()

        # Verify empty directories were cleaned up
        assert not (temp_dir / "nested" / "deep").exists()
        assert not (temp_dir / "nested").exists()

    def test_delete_file_preserves_non_empty_directories(
        self, storage: FileSystemBlobStorage, temp_dir: Path
    ) -> None:
        """Test that non-empty directories are preserved after file deletion."""
        # Create two files in the same directory
        file1_path = temp_dir / "shared" / "file1.txt"
        file2_path = temp_dir / "shared" / "file2.txt"
        file1_path.parent.mkdir(parents=True)
        file1_path.write_bytes(b"content1")
        file2_path.write_bytes(b"content2")

        # Delete only one file
        result = storage.delete_file("shared/file1.txt")

        assert result.is_ok()
        assert result.unwrap() is True
        assert not file1_path.exists()
        assert file2_path.exists()  # Other file still exists

        # Directory should still exist
        assert (temp_dir / "shared").exists()

    def test_delete_file_os_error(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test delete file handles OS errors."""
        object_name = "error.txt"

        # Create file
        file_path = temp_dir / object_name
        file_path.write_bytes(b"content")

        with patch("pathlib.Path.unlink", side_effect=OSError("Delete error")):
            result = storage.delete_file(object_name)

        assert result.is_err()
        error = result.err()
        assert isinstance(error, BlobStorageError)
        assert error.code == "DELETE_ERROR"
        assert "Delete failed" in error.message

    def test_file_exists_true(self, storage: FileSystemBlobStorage, temp_dir: Path) -> None:
        """Test file_exists returns True for existing files."""
        object_name = "exists.txt"

        # Create file
        file_path = temp_dir / object_name
        file_path.write_bytes(b"content")

        assert storage.file_exists(object_name) is True

    def test_file_exists_false(self, storage: FileSystemBlobStorage) -> None:
        """Test file_exists returns False for non-existing files."""
        assert storage.file_exists("nonexistent.txt") is False

    def test_file_exists_with_subdirectory(
        self, storage: FileSystemBlobStorage, temp_dir: Path
    ) -> None:
        """Test file_exists works with subdirectories."""
        object_name = "folder/file.txt"

        # Create file in subdirectory
        file_path = temp_dir / object_name
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"content")

        assert storage.file_exists(object_name) is True
        assert storage.file_exists("folder/nonexistent.txt") is False

    def test_calculate_hash(self, storage: FileSystemBlobStorage) -> None:
        """Test SHA-256 hash calculation."""
        content = b"Hello, World!"
        file_obj = io.BytesIO(content)

        hash_value = storage.calculate_hash(file_obj)

        # SHA-256 of "Hello, World!" (note the comma and space)
        expected_hash = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        assert hash_value == expected_hash

        # Verify file pointer was reset
        assert file_obj.tell() == 0

    def test_calculate_hash_empty_file(self, storage: FileSystemBlobStorage) -> None:
        """Test hash calculation for empty file."""
        file_obj = io.BytesIO(b"")

        hash_value = storage.calculate_hash(file_obj)

        # SHA-256 of empty string
        expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected_hash

    def test_calculate_hash_large_file(self, storage: FileSystemBlobStorage) -> None:
        """Test hash calculation for larger file (tests chunked reading)."""
        # Create content larger than the 4096 byte chunk size
        content = b"A" * 10000
        file_obj = io.BytesIO(content)

        hash_value = storage.calculate_hash(file_obj)

        # Verify it's a valid SHA-256 hash
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

        # Verify file pointer was reset
        assert file_obj.tell() == 0

    def test_get_full_path_creates_parent_directories(
        self, storage: FileSystemBlobStorage, temp_dir: Path
    ) -> None:
        """Test that _get_full_path creates parent directories."""
        object_name = "deep/nested/path/file.txt"

        full_path = storage._get_full_path(object_name)

        assert full_path == temp_dir / object_name
        assert full_path.parent.exists()
        assert full_path.parent.is_dir()
