"""Unit tests for FileSystemBlobStorage."""

import tempfile
from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import pytest
from src.infrastructure.storage import FileSystemBlobStorage


@pytest.fixture
def temp_storage_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for storage tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage(temp_storage_dir: Path) -> FileSystemBlobStorage:
    """Create a FileSystemBlobStorage instance with temporary directory."""
    return FileSystemBlobStorage(base_path=str(temp_storage_dir))


def test_upload_file(storage: FileSystemBlobStorage, temp_storage_dir: Path) -> None:
    """Test uploading a file to file system storage."""
    file_content = b"Test file content"
    file_obj = BytesIO(file_content)
    object_name = "test.txt"

    result = storage.upload_file(file_obj, object_name)

    assert result == object_name
    assert (temp_storage_dir / object_name).exists()
    assert (temp_storage_dir / object_name).read_bytes() == file_content


def test_upload_file_with_nested_path(
    storage: FileSystemBlobStorage, temp_storage_dir: Path
) -> None:
    """Test uploading a file with nested path."""
    file_content = b"Nested file content"
    file_obj = BytesIO(file_content)
    object_name = "user123/documents/test.pdf"

    result = storage.upload_file(file_obj, object_name)

    assert result == object_name
    full_path = temp_storage_dir / "user123" / "documents" / "test.pdf"
    assert full_path.exists()
    assert full_path.read_bytes() == file_content


def test_download_file(storage: FileSystemBlobStorage) -> None:
    """Test downloading a file from file system storage."""
    file_content = b"Download test content"
    file_obj = BytesIO(file_content)
    object_name = "download_test.txt"

    storage.upload_file(file_obj, object_name)
    downloaded_content = storage.download_file(object_name)

    assert downloaded_content == file_content


def test_download_file_not_found(storage: FileSystemBlobStorage) -> None:
    """Test downloading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        storage.download_file("nonexistent.txt")

    assert "File not found: nonexistent.txt" in str(exc_info.value)


def test_delete_file(storage: FileSystemBlobStorage, temp_storage_dir: Path) -> None:
    """Test deleting a file from file system storage."""
    file_content = b"Delete test content"
    file_obj = BytesIO(file_content)
    object_name = "delete_test.txt"

    storage.upload_file(file_obj, object_name)
    assert (temp_storage_dir / object_name).exists()

    result = storage.delete_file(object_name)

    assert result is True
    assert not (temp_storage_dir / object_name).exists()


def test_delete_file_not_found(storage: FileSystemBlobStorage) -> None:
    """Test deleting a non-existent file returns False."""
    result = storage.delete_file("nonexistent.txt")
    assert result is False


def test_delete_file_cleans_up_empty_directories(
    storage: FileSystemBlobStorage, temp_storage_dir: Path
) -> None:
    """Test that deleting a file cleans up empty parent directories."""
    file_content = b"Cleanup test content"
    file_obj = BytesIO(file_content)
    object_name = "user123/documents/subfolder/test.txt"

    storage.upload_file(file_obj, object_name)

    user_dir = temp_storage_dir / "user123"
    docs_dir = user_dir / "documents"
    subfolder_dir = docs_dir / "subfolder"
    assert subfolder_dir.exists()

    storage.delete_file(object_name)

    # All empty parent directories should be cleaned up
    assert not subfolder_dir.exists()
    assert not docs_dir.exists()
    assert not user_dir.exists()


def test_file_exists(storage: FileSystemBlobStorage) -> None:
    """Test checking if a file exists."""
    object_name = "exists_test.txt"

    # File should not exist initially
    assert storage.file_exists(object_name) is False

    # Upload file
    file_obj = BytesIO(b"Exists test content")
    storage.upload_file(file_obj, object_name)

    # File should now exist
    assert storage.file_exists(object_name) is True


def test_calculate_hash(storage: FileSystemBlobStorage) -> None:
    """Test calculating SHA-256 hash of a file."""
    file_content = b"Hash test content"
    file_obj = BytesIO(file_content)

    hash_result = storage.calculate_hash(file_obj)

    # Verify it's a valid SHA-256 hash (64 hex characters)
    assert len(hash_result) == 64
    assert all(c in "0123456789abcdef" for c in hash_result)

    # Verify hash is consistent
    file_obj.seek(0)
    hash_result2 = storage.calculate_hash(file_obj)
    assert hash_result == hash_result2


def test_calculate_hash_resets_file_position(storage: FileSystemBlobStorage) -> None:
    """Test that calculate_hash resets file position to beginning."""
    file_content = b"Position test content"
    file_obj = BytesIO(file_content)

    # Move to end of file
    file_obj.seek(0, 2)
    assert file_obj.tell() != 0

    storage.calculate_hash(file_obj)

    # File position should be reset to beginning
    assert file_obj.tell() == 0


def test_upload_file_resets_file_position(storage: FileSystemBlobStorage) -> None:
    """Test that upload_file resets file position to beginning."""
    file_content = b"Upload position test"
    file_obj = BytesIO(file_content)

    # Move to middle of file
    file_obj.seek(5)

    storage.upload_file(file_obj, "position_test.txt")

    # Verify entire file was uploaded, not just from position 5
    downloaded = storage.download_file("position_test.txt")
    assert downloaded == file_content


def test_multiple_files_in_same_directory(
    storage: FileSystemBlobStorage, temp_storage_dir: Path
) -> None:
    """Test uploading multiple files to the same directory."""
    file1_content = b"File 1 content"
    file2_content = b"File 2 content"

    storage.upload_file(BytesIO(file1_content), "docs/file1.txt")
    storage.upload_file(BytesIO(file2_content), "docs/file2.txt")

    assert storage.file_exists("docs/file1.txt")
    assert storage.file_exists("docs/file2.txt")
    assert storage.download_file("docs/file1.txt") == file1_content
    assert storage.download_file("docs/file2.txt") == file2_content


def test_overwrite_existing_file(storage: FileSystemBlobStorage) -> None:
    """Test that uploading to an existing object name overwrites the file."""
    object_name = "overwrite_test.txt"

    # Upload first version
    storage.upload_file(BytesIO(b"Original content"), object_name)
    assert storage.download_file(object_name) == b"Original content"

    # Upload second version with same name
    storage.upload_file(BytesIO(b"Updated content"), object_name)
    assert storage.download_file(object_name) == b"Updated content"
