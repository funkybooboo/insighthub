"""Integration tests for blob storage with MinIO testcontainer."""

from io import BytesIO

import pytest

from src.storage.blob_storage import S3BlobStorage


def test_upload_and_download_file(blob_storage: S3BlobStorage) -> None:
    """Test uploading and downloading a file from blob storage."""
    # Create test file
    test_content = b"This is test content for blob storage"
    file_obj = BytesIO(test_content)

    # Upload file
    object_name = "test/file.txt"
    result = blob_storage.upload_file(file_obj, object_name)

    assert result == object_name

    # Download file
    downloaded_content = blob_storage.download_file(object_name)

    assert downloaded_content == test_content


def test_file_exists(blob_storage: S3BlobStorage) -> None:
    """Test checking if a file exists in blob storage."""
    # Upload file
    file_obj = BytesIO(b"test content")
    object_name = "test/exists.txt"
    blob_storage.upload_file(file_obj, object_name)

    # Check if file exists
    assert blob_storage.file_exists(object_name) is True
    assert blob_storage.file_exists("nonexistent/file.txt") is False


def test_delete_file(blob_storage: S3BlobStorage) -> None:
    """Test deleting a file from blob storage."""
    # Upload file
    file_obj = BytesIO(b"test content")
    object_name = "test/delete.txt"
    blob_storage.upload_file(file_obj, object_name)

    # Verify file exists
    assert blob_storage.file_exists(object_name) is True

    # Delete file
    result = blob_storage.delete_file(object_name)

    assert result is True
    assert blob_storage.file_exists(object_name) is False


def test_calculate_hash(blob_storage: S3BlobStorage) -> None:
    """Test calculating SHA-256 hash of a file."""
    content = b"test content for hashing"
    file_obj = BytesIO(content)

    hash1 = blob_storage.calculate_hash(file_obj)

    # Hash should be consistent
    file_obj.seek(0)
    hash2 = blob_storage.calculate_hash(file_obj)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 produces 64 character hex string


def test_upload_large_file(blob_storage: S3BlobStorage) -> None:
    """Test uploading a larger file (1MB)."""
    # Create 1MB file
    large_content = b"x" * (1024 * 1024)
    file_obj = BytesIO(large_content)

    # Upload file
    object_name = "test/large_file.bin"
    result = blob_storage.upload_file(file_obj, object_name)

    assert result == object_name

    # Verify by downloading
    downloaded = blob_storage.download_file(object_name)
    assert len(downloaded) == len(large_content)
    assert downloaded == large_content


def test_upload_with_nested_path(blob_storage: S3BlobStorage) -> None:
    """Test uploading files with nested directory structure."""
    file_obj = BytesIO(b"nested content")
    object_name = "level1/level2/level3/file.txt"

    result = blob_storage.upload_file(file_obj, object_name)

    assert result == object_name
    assert blob_storage.file_exists(object_name) is True


def test_duplicate_upload_overwrites(blob_storage: S3BlobStorage) -> None:
    """Test that uploading to same key overwrites the file."""
    object_name = "test/overwrite.txt"

    # Upload first version
    file_obj1 = BytesIO(b"version 1")
    blob_storage.upload_file(file_obj1, object_name)

    # Upload second version with same key
    file_obj2 = BytesIO(b"version 2")
    blob_storage.upload_file(file_obj2, object_name)

    # Download and verify it's the second version
    downloaded = blob_storage.download_file(object_name)
    assert downloaded == b"version 2"
