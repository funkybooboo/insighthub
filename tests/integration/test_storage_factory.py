"""Integration tests for the Storage Factory component."""

import tempfile

import pytest
from returns.result import Success
from testcontainers.minio import MinioContainer

from src.infrastructure.storage.factory import create_blob_storage
from src.infrastructure.storage.file_system_storage import FileSystemBlobStorage
from src.infrastructure.storage.s3_storage import S3BlobStorage


@pytest.mark.integration
class TestStorageFactoryIntegration:
    """Integration tests for the Storage Factory component."""

    @pytest.fixture(scope="class")
    def minio_container(self):
        """Fixture to spin up a Minio container for testing."""
        with MinioContainer("minio/minio:latest") as container:
            yield container

    @pytest.fixture(scope="function")
    def filesystem_base_path(self):
        """Fixture to create a temporary directory for FileSystemBlobStorage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_blob_storage_filesystem(self, filesystem_base_path: str):
        """Test that create_blob_storage correctly creates a FileSystemBlobStorage."""
        # Act
        storage = create_blob_storage(storage_type="filesystem", base_path=filesystem_base_path)

        # Assert
        assert isinstance(storage, FileSystemBlobStorage)

        # Test basic operations
        key = "test_file.txt"
        data = b"Hello, filesystem!"
        storage.upload(key, data, "text/plain")
        assert storage.exists(key) is True
        downloaded = storage.download(key)
        assert isinstance(downloaded, Success)
        assert downloaded.unwrap() == data
        storage.delete(key)
        assert storage.exists(key) is False

    def test_create_blob_storage_s3(self, minio_container: MinioContainer):
        """Test that create_blob_storage correctly creates an S3BlobStorage."""
        # Arrange
        endpoint = minio_container.get_config()["endpoint"]
        access_key = minio_container.get_config()["access_key"]
        secret_key = minio_container.get_config()["secret_key"]
        bucket_name = "factory-test-bucket"

        # Act
        storage = create_blob_storage(
            storage_type="s3",
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            secure=False,
        )

        # Assert
        assert isinstance(storage, S3BlobStorage)
        assert storage.bucket_name == bucket_name

        # Test basic operations
        key = "s3_test_object.txt"
        data = b"Hello, S3!"
        storage.upload(key, data, "text/plain")
        assert storage.exists(key) is True
        downloaded = storage.download(key)
        assert isinstance(downloaded, Success)
        assert downloaded.unwrap() == data
        storage.delete(key)
        assert storage.exists(key) is False

    def test_create_blob_storage_unsupported_type(self):
        """Test that create_blob_storage raises ValueError for unsupported types."""
        with pytest.raises(ValueError, match="Unsupported storage type"):
            create_blob_storage(storage_type="unsupported")

    def test_create_blob_storage_s3_missing_params(self):
        """Test that create_blob_storage raises ValueError for missing S3 parameters."""
        with pytest.raises(
            ValueError, match="S3 storage requires endpoint, access_key, and secret_key"
        ):
            create_blob_storage(storage_type="s3", endpoint="test")
        with pytest.raises(
            ValueError, match="S3 storage requires endpoint, access_key, and secret_key"
        ):
            create_blob_storage(storage_type="s3", access_key="test")
        with pytest.raises(
            ValueError, match="S3 storage requires endpoint, access_key, and secret_key"
        ):
            create_blob_storage(storage_type="s3", secret_key="test")
