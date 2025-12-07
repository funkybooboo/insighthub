"""Integration tests for S3BlobStorage with a real Minio S3 instance."""

from collections.abc import Generator

import pytest
from returns.result import Failure, Success
from testcontainers.minio import MinioContainer

from src.infrastructure.storage.s3_storage import S3BlobStorage


@pytest.mark.integration
class TestS3BlobStorageIntegration:
    """S3 integration tests for the S3BlobStorage component."""

    @pytest.fixture(scope="class")
    def minio_container(self):
        """Fixture to spin up a Minio container for testing."""
        with MinioContainer("minio/minio:latest") as container:
            yield container

    @pytest.fixture(scope="function")
    def s3_storage_instance(
        self, minio_container: MinioContainer
    ) -> Generator[S3BlobStorage, None, None]:
        """Fixture to create an S3BlobStorage instance connected to the test container."""
        endpoint = minio_container.get_config()["endpoint"]
        endpoint = endpoint.replace("https://", "").replace("http://", "")
        access_key = minio_container.get_config()["access_key"]
        secret_key = minio_container.get_config()["secret_key"]
        bucket_name = "test-bucket"

        storage = S3BlobStorage(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            secure=False,  # Minio http
        )
        # The client is lazy, so we need to trigger its creation
        _ = storage.client
        yield storage

    def test_s3_connection(self, s3_storage_instance: S3BlobStorage):
        """Test that the S3 connection is established and the bucket is created."""
        assert s3_storage_instance.client is not None
        # _ensure_bucket is called on client creation, check if bucket exists
        try:
            s3_storage_instance.client.head_bucket(Bucket=s3_storage_instance.bucket_name)
        except Exception as e:
            pytest.fail(f"Bucket '{s3_storage_instance.bucket_name}' not found: {e}")

    def test_upload_and_download(self, s3_storage_instance: S3BlobStorage):
        """Test that we can upload and download data from S3."""
        # Arrange
        key = "test_object.txt"
        data = b"This is a test file."
        content_type = "text/plain"

        # Act
        url_result = s3_storage_instance.upload(key, data, content_type)
        downloaded_data_result = s3_storage_instance.download(key)

        # Assert
        assert isinstance(url_result, Success)
        url = url_result.unwrap()
        assert isinstance(url, str)
        assert s3_storage_instance.bucket_name in url
        assert key in url
        assert isinstance(downloaded_data_result, Success)
        assert downloaded_data_result.unwrap() == data

    def test_download_nonexistent_object(self, s3_storage_instance: S3BlobStorage):
        """Test that downloading a nonexistent object returns a Failure result."""
        result = s3_storage_instance.download("nonexistent_object")
        assert isinstance(result, Failure)

    def test_delete(self, s3_storage_instance: S3BlobStorage):
        """Test that we can delete an object from S3."""
        # Arrange
        key = "object_to_delete.txt"
        data = b"Some data"
        s3_storage_instance.upload(key, data)
        assert s3_storage_instance.exists(key) is True

        # Act
        deleted = s3_storage_instance.delete(key)

        # Assert
        assert deleted is True
        assert s3_storage_instance.exists(key) is False

    def test_exists(self, s3_storage_instance: S3BlobStorage):
        """Test the 'exists' method."""
        # Arrange
        key = "existing_object.txt"
        data = b"Some other data"
        s3_storage_instance.upload(key, data)

        # Act & Assert
        assert s3_storage_instance.exists(key) is True
        assert s3_storage_instance.exists("nonexistent_object") is False

    def test_get_url(self, s3_storage_instance: S3BlobStorage):
        """Test that we can get a presigned URL for an object."""
        # Arrange
        key = "url_test_object.txt"
        data = b"URL test data"
        s3_storage_instance.upload(key, data)

        # Act
        url_result = s3_storage_instance.get_url(key)

        # Assert
        assert isinstance(url_result, Success)
        url = url_result.unwrap()
        assert isinstance(url, str)
        assert s3_storage_instance.bucket_name in url
        assert key in url
