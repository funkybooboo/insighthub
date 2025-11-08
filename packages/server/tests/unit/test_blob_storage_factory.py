"""Unit tests for blob storage factory."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from src.infrastructure.storage import (
    BlobStorageType,
    FileSystemBlobStorage,
    InMemoryBlobStorage,
    MinioBlobStorage,
    create_blob_storage,
)


class TestBlobStorageFactory:
    """Test cases for blob storage factory."""

    def test_create_s3_storage_explicitly(self) -> None:
        """Test creating S3/MinIO storage with explicit type."""
        with (
            patch("src.config.S3_ENDPOINT_URL", "http://minio:9000"),
            patch("src.config.S3_ACCESS_KEY", "test_key"),
            patch("src.config.S3_SECRET_KEY", "test_secret"),
            patch("src.config.S3_BUCKET_NAME", "test-bucket"),
            patch("src.infrastructure.storage.minio_blob_storage.boto3.client"),
        ):
            storage = create_blob_storage(storage_type=BlobStorageType.S3)
            assert isinstance(storage, MinioBlobStorage)

    def test_create_file_system_storage_explicitly(self) -> None:
        """Test creating file system storage with explicit type."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("src.config.FILE_SYSTEM_STORAGE_PATH", tmpdir),
        ):
            storage = create_blob_storage(storage_type=BlobStorageType.FILE_SYSTEM)
            assert isinstance(storage, FileSystemBlobStorage)
            assert storage.base_path == Path(tmpdir)

    def test_create_in_memory_storage_explicitly(self) -> None:
        """Test creating in-memory storage with explicit type."""
        storage = create_blob_storage(storage_type=BlobStorageType.IN_MEMORY)

        assert isinstance(storage, InMemoryBlobStorage)
        assert hasattr(storage, "storage")
        assert isinstance(storage.storage, dict)

    def test_create_storage_from_config_s3(self) -> None:
        """Test creating storage from config (S3 type)."""
        with (
            patch("src.config.BLOB_STORAGE_TYPE", "s3"),
            patch("src.config.S3_ENDPOINT_URL", "http://localhost:9000"),
            patch("src.config.S3_ACCESS_KEY", "admin"),
            patch("src.config.S3_SECRET_KEY", "password"),
            patch("src.config.S3_BUCKET_NAME", "files"),
            patch("src.infrastructure.storage.minio_blob_storage.boto3.client"),
        ):
            storage = create_blob_storage()
            assert isinstance(storage, MinioBlobStorage)

    def test_create_storage_from_config_file_system(self) -> None:
        """Test creating storage from config (file system type)."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("src.config.BLOB_STORAGE_TYPE", "file_system"),
            patch("src.config.FILE_SYSTEM_STORAGE_PATH", tmpdir),
        ):
            storage = create_blob_storage()
            assert isinstance(storage, FileSystemBlobStorage)

    def test_create_storage_from_config_in_memory(self) -> None:
        """Test creating storage from config (in-memory type)."""
        with patch("src.config.BLOB_STORAGE_TYPE", "in_memory"):
            storage = create_blob_storage()

            assert isinstance(storage, InMemoryBlobStorage)

    def test_invalid_storage_type_raises_error(self) -> None:
        """Test that invalid storage type raises ValueError."""
        with patch("src.config.BLOB_STORAGE_TYPE", "invalid_type"):
            with pytest.raises(ValueError) as exc_info:
                create_blob_storage()

            assert "invalid_type" in str(exc_info.value)

    def test_storage_type_enum_values(self) -> None:
        """Test that BlobStorageType enum has expected values."""
        assert BlobStorageType.S3.value == "s3"
        assert BlobStorageType.FILE_SYSTEM.value == "file_system"
        assert BlobStorageType.IN_MEMORY.value == "in_memory"

    def test_file_system_storage_creates_base_directory(self) -> None:
        """Test that file system storage creates base directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent" / "storage"
            assert not storage_path.exists()

            with patch("src.config.FILE_SYSTEM_STORAGE_PATH", str(storage_path)):
                storage = create_blob_storage(storage_type=BlobStorageType.FILE_SYSTEM)

                assert isinstance(storage, FileSystemBlobStorage)
                assert storage_path.exists()
                assert storage_path.is_dir()
