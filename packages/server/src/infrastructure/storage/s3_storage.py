"""S3-compatible blob storage implementation using MinIO."""

import os
from typing import Optional
from urllib.parse import urljoin

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

from .storage import BlobStorage


class S3BlobStorage(BlobStorage):
    """S3-compatible blob storage using MinIO client."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = True,
        region: Optional[str] = None,
    ):
        """
        Initialize S3 blob storage.

        Args:
            endpoint: S3 endpoint URL (e.g., "localhost:9000" for MinIO)
            access_key: S3 access key
            secret_key: S3 secret key
            bucket_name: S3 bucket name
            secure: Whether to use HTTPS (default: True)
            region: S3 region (optional)
        """
        if not MINIO_AVAILABLE:
            raise ImportError("minio package is required for S3BlobStorage")

        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.secure = secure

        # Initialize MinIO client
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
        )

        # Ensure bucket exists
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Ensure the bucket exists, create it if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise RuntimeError(f"Failed to create/access bucket {self.bucket_name}: {e}")

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload data to S3 storage.

        Args:
            key: Unique identifier for the blob
            data: Binary data to store
            content_type: MIME type of the data

        Returns:
            str: URL to access the uploaded blob
        """
        from io import BytesIO

        try:
            # Upload data
            data_stream = BytesIO(data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=key,
                data=data_stream,
                length=len(data),
                content_type=content_type,
            )

            # Return the URL
            return self.get_url(key)

        except S3Error as e:
            raise RuntimeError(f"Failed to upload {key}: {e}")

    def download(self, key: str) -> bytes:
        """
        Download data from S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bytes: Binary data from storage

        Raises:
            FileNotFoundError: If blob doesn't exist
        """
        try:
            response = self.client.get_object(self.bucket_name, key)
            return response.read()

        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"Blob {key} not found")
            raise RuntimeError(f"Failed to download {key}: {e}")

    def delete(self, key: str) -> bool:
        """
        Delete a blob from S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            self.client.remove_object(self.bucket_name, key)
            return True

        except S3Error as e:
            if e.code == "NoSuchKey":
                return False  # Already doesn't exist
            raise RuntimeError(f"Failed to delete {key}: {e}")

    def exists(self, key: str) -> bool:
        """
        Check if a blob exists in S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if blob exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, key)
            return True

        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise RuntimeError(f"Failed to check existence of {key}: {e}")

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for accessing the blob.

        Args:
            key: Unique identifier for the blob
            expires_in: URL expiration time in seconds

        Returns:
            str: Signed URL for blob access
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=key,
                expires=expires_in,
            )
            return url

        except S3Error as e:
            raise RuntimeError(f"Failed to generate URL for {key}: {e}")