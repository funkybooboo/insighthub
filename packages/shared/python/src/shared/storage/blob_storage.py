"""Blob storage interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO

from shared.types.result import Result


class BlobStorageError:
    """Error type for blob storage failures."""

    def __init__(self, message: str, code: str = "STORAGE_ERROR") -> None:
        """
        Initialize blob storage error.

        Args:
            message: Error message
            code: Error code for categorization
        """
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class BlobStorage(ABC):
    """
    Abstract base class for blob storage.

    Implementations: S3BlobStorage, FileSystemBlobStorage, InMemoryBlobStorage
    """

    @abstractmethod
    def upload_file(
        self, file_obj: BinaryIO, object_name: str
    ) -> Result[str, BlobStorageError]:
        """
        Upload a file to blob storage.

        Args:
            file_obj: File-like object to upload
            object_name: Name/key for the object in storage

        Returns:
            Result containing object key on success, or BlobStorageError on failure
        """
        pass

    @abstractmethod
    def download_file(self, object_name: str) -> Result[bytes, BlobStorageError]:
        """
        Download a file from blob storage.

        Args:
            object_name: Name/key of the object to download

        Returns:
            Result containing file content as bytes, or BlobStorageError on failure
        """
        pass

    @abstractmethod
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from blob storage.

        Args:
            object_name: Name/key of the object to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in blob storage.

        Args:
            object_name: Name/key of the object to check

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_obj: File-like object

        Returns:
            SHA-256 hash hex digest
        """
        pass
