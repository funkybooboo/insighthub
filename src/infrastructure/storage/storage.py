"""Storage infrastructure for file operations."""

from abc import ABC, abstractmethod

from returns.result import Result

from src.infrastructure.types.errors import StorageError


class BlobStorage(ABC):
    """Abstract base class for blob storage operations."""

    @abstractmethod
    def upload(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> Result[str, StorageError]:
        """
        Upload data to storage.

        Args:
            key: Unique identifier for the blob
            data: Binary data to store
            content_type: MIME type of the data

        Returns:
            Result with URL or path to access the uploaded blob, or StorageError
        """
        pass

    @abstractmethod
    def download(self, key: str) -> Result[bytes, StorageError]:
        """
        Download data from storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            Result with binary data from storage, or StorageError
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a blob from storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a blob exists in storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if blob exists, False otherwise
        """
        pass

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 3600) -> Result[str, StorageError]:
        """
        Get a signed URL for accessing the blob.

        Args:
            key: Unique identifier for the blob
            expires_in: URL expiration time in seconds

        Returns:
            Result with signed URL for blob access, or StorageError
        """
        pass
