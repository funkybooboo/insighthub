"""MinIO/S3 blob storage implementation."""

import hashlib
from typing import TYPE_CHECKING, BinaryIO

from shared.logger import create_logger
from shared.types.result import Err, Ok, Result

from .blob_storage import BlobStorage, BlobStorageError

if TYPE_CHECKING:
    from minio import Minio as MinioClient

try:
    from minio import Minio
    from minio.error import S3Error

    MINIO_AVAILABLE = True
except ImportError:
    Minio = None
    S3Error = Exception
    MINIO_AVAILABLE = False

logger = create_logger(__name__)


class S3BlobStorage(BlobStorage):
    """
    MinIO/S3-compatible blob storage implementation.

    Used by server and workers to upload/download documents.

    Example:
        storage = S3BlobStorage(
            endpoint="minio:9000",
            access_key="insighthub",
            secret_key="insighthub_dev_secret",
            bucket_name="documents",
            secure=False,
        )
        result = storage.upload_file(file_obj, "hash/document.pdf")
        if result.is_ok():
            object_key = result.unwrap()
    """

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool,
    ) -> None:
        """
        Initialize MinIO storage.

        Args:
            endpoint: MinIO endpoint (e.g., "minio:9000")
            access_key: Access key
            secret_key: Secret key
            bucket_name: Bucket name
            secure: Use HTTPS

        Raises:
            RuntimeError: If minio library is not available
        """
        if not MINIO_AVAILABLE or Minio is None:
            raise RuntimeError("minio library not available. Install: pip install minio")

        self._endpoint = endpoint
        self._bucket_name = bucket_name

        self._client: "MinioClient" = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self._client.bucket_exists(self._bucket_name):
                self._client.make_bucket(self._bucket_name)
                logger.info("Created bucket", bucket=self._bucket_name)
            else:
                logger.info("Bucket exists", bucket=self._bucket_name)
        except S3Error as e:
            logger.error("Error checking/creating bucket", error=str(e))
            raise RuntimeError(f"Failed to ensure bucket exists: {e}") from e

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> Result[str, BlobStorageError]:
        """Upload file to MinIO."""
        try:
            file_obj.seek(0, 2)
            file_size = file_obj.tell()
            file_obj.seek(0)

            self._client.put_object(
                bucket_name=self._bucket_name,
                object_name=object_name,
                data=file_obj,
                length=file_size,
            )

            logger.info("Uploaded file", object_name=object_name, size_bytes=file_size)
            return Ok(object_name)

        except S3Error as e:
            logger.error("Error uploading file", object_name=object_name, error=str(e))
            return Err(BlobStorageError(f"Upload failed: {e}", code="UPLOAD_ERROR"))

    def download_file(self, object_name: str) -> Result[bytes, BlobStorageError]:
        """Download file from MinIO."""
        try:
            response = self._client.get_object(
                bucket_name=self._bucket_name, object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()

            logger.info("Downloaded file", object_name=object_name, size_bytes=len(data))
            return Ok(data)

        except S3Error as e:
            logger.error("Error downloading file", object_name=object_name, error=str(e))
            return Err(BlobStorageError(f"Download failed: {e}", code="DOWNLOAD_ERROR"))

    def delete_file(self, object_name: str) -> Result[bool, BlobStorageError]:
        """Delete file from MinIO."""
        try:
            # Check if file exists first
            exists = self.file_exists(object_name)
            if not exists:
                return Ok(False)

            self._client.remove_object(bucket_name=self._bucket_name, object_name=object_name)
            logger.info("Deleted file", object_name=object_name)
            return Ok(True)
        except S3Error as e:
            logger.error("Error deleting file", object_name=object_name, error=str(e))
            return Err(BlobStorageError(f"Delete failed: {e}", code="DELETE_ERROR"))

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            self._client.stat_object(bucket_name=self._bucket_name, object_name=object_name)
            return True
        except S3Error:
            return False

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of file."""
        file_obj.seek(0)
        sha256_hash = hashlib.sha256()

        for chunk in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(chunk)

        file_obj.seek(0)
        return sha256_hash.hexdigest()
