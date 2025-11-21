"""MinIO blob storage implementation."""

import hashlib
import logging
from io import BytesIO
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from .blob_storage import BlobStorage

logger = logging.getLogger(__name__)


class S3BlobStorage(BlobStorage):
    """
    MinIO/S3-compatible blob storage implementation.
    
    Used by server and workers to upload/download documents.
    
    Example:
        storage = MinIOBlobStorage(
            endpoint="minio:9000",
            access_key="insighthub",
            secret_key="insighthub_dev_secret",
            bucket_name="documents",
            secure=False,  # True for HTTPS
        )
        
        # Upload
        with open("document.pdf", "rb") as f:
            storage.upload_file(f, "hash/document.pdf")
        
        # Download
        content = storage.download_file("hash/document.pdf")
    """

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ):
        """
        Initialize MinIO storage.

        Args:
            endpoint: MinIO endpoint (e.g., "minio:9000")
            access_key: Access key
            secret_key: Secret key
            bucket_name: Bucket name
            secure: Use HTTPS
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure

        # Create MinIO client
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> str:
        """
        Upload file to MinIO.

        Args:
            file_obj: File-like object
            object_name: Object key (e.g., "hash/document.pdf")

        Returns:
            Object key
        """
        try:
            # Get file size
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(0)  # Reset to beginning

            # Upload
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_obj,
                length=file_size,
            )

            logger.info(f"Uploaded file: {object_name} ({file_size} bytes)")
            return object_name

        except S3Error as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """
        Download file from MinIO.

        Args:
            object_name: Object key

        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()

            logger.info(f"Downloaded file: {object_name} ({len(data)} bytes)")
            return data

        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        Delete file from MinIO.

        Args:
            object_name: Object key

        Returns:
            True if successful
        """
        try:
            self.client.remove_object(bucket_name=self.bucket_name, object_name=object_name)
            logger.info(f"Deleted file: {object_name}")
            return True

        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            return False

    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in MinIO.

        Args:
            object_name: Object key

        Returns:
            True if exists
        """
        try:
            self.client.stat_object(bucket_name=self.bucket_name, object_name=object_name)
            return True
        except S3Error:
            return False

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """
        Calculate SHA-256 hash of file.

        Args:
            file_obj: File-like object

        Returns:
            SHA-256 hex digest
        """
        file_obj.seek(0)
        sha256_hash = hashlib.sha256()

        # Read file in chunks to handle large files
        for chunk in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(chunk)

        file_obj.seek(0)
        return sha256_hash.hexdigest()
