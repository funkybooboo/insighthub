"""Local filesystem blob storage implementation."""

from pathlib import Path

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.types.errors import StorageError

from .storage import BlobStorage

logger = create_logger(__name__)


class FileSystemBlobStorage(BlobStorage):
    """Local filesystem blob storage implementation."""

    def __init__(self, base_path: str):
        """
        Initialize filesystem blob storage.

        Args:
            base_path: Base directory path for storing files
        """
        self.base_path = Path(base_path).resolve()

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> Result[Path, StorageError]:
        """Get the full file path for a given key."""
        # Ensure key doesn't contain path traversal attacks
        key = key.replace("\\", "/")  # Normalize path separators

        # Remove leading slashes and resolve the path safely
        key_parts = [part for part in key.split("/") if part and part not in (".", "..")]
        file_path = self.base_path / Path(*key_parts)

        # Ensure the resolved path is still within base_path
        try:
            file_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            return Failure(
                StorageError(f"Invalid key: {key} - path traversal detected", operation="validate")
            )

        return Success(file_path)

    def upload(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> Result[str, StorageError]:
        """
        Upload data to filesystem storage.

        Args:
            key: Unique identifier for the blob
            data: Binary data to store
            content_type: MIME type of the data

        Returns:
            Result with file path to access the uploaded blob, or StorageError
        """
        file_path_result = self._get_file_path(key)
        if isinstance(file_path_result, Failure):
            logger.error(f"Invalid storage key: {key}")
            return file_path_result

        file_path = file_path_result.unwrap()

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write data to file
            with open(file_path, "wb") as f:
                f.write(data)

            return Success(str(file_path))
        except OSError as e:
            logger.error(f"Filesystem error during upload: {e}")
            return Failure(StorageError(str(e), operation="upload"))
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return Failure(StorageError(str(e), operation="upload"))

    def download(self, key: str) -> Result[bytes, StorageError]:
        """
        Download data from filesystem storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            Result with binary data from storage, or StorageError
        """
        file_path_result = self._get_file_path(key)
        if isinstance(file_path_result, Failure):
            logger.error(f"Invalid storage key: {key}")
            return file_path_result

        file_path = file_path_result.unwrap()

        if not file_path.exists():
            logger.error(f"Blob not found: {key}")
            return Failure(StorageError(f"Blob {key} not found", operation="download"))

        try:
            with open(file_path, "rb") as f:
                return Success(f.read())
        except OSError as e:
            logger.error(f"Filesystem error during download: {e}")
            return Failure(StorageError(str(e), operation="download"))
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return Failure(StorageError(str(e), operation="download"))

    def delete(self, key: str) -> bool:
        """
        Delete a blob from filesystem storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        file_path_result = self._get_file_path(key)
        if isinstance(file_path_result, Failure):
            return False

        file_path = file_path_result.unwrap()

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a blob exists in filesystem storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if blob exists, False otherwise
        """
        file_path_result = self._get_file_path(key)
        if isinstance(file_path_result, Failure):
            return False

        file_path = file_path_result.unwrap()
        return file_path.exists() and file_path.is_file()

    def get_url(self, key: str, expires_in: int = 3600) -> Result[str, StorageError]:
        """
        Get a file path URL for accessing the blob.

        Args:
            key: Unique identifier for the blob
            expires_in: URL expiration time in seconds (ignored for filesystem)

        Returns:
            Result with file path URL for blob access, or StorageError
        """
        file_path_result = self._get_file_path(key)
        if isinstance(file_path_result, Failure):
            return file_path_result

        file_path = file_path_result.unwrap()
        return Success(f"file://{file_path}")
