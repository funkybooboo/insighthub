"""Blob storage interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class BlobStorage(ABC):
    """
    Abstract base class for blob storage.
    
    Implementations: MinIO, S3, FileSystem, InMemory
    """

    @abstractmethod
    def upload_file(self, file_obj: BinaryIO, object_name: str) -> str:
        """
        Upload a file to blob storage.

        Args:
            file_obj: File-like object to upload
            object_name: Name/key for the object in storage

        Returns:
            URL or key to access the uploaded file
        """
        pass

    @abstractmethod
    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from blob storage.

        Args:
            object_name: Name/key of the object to download

        Returns:
            File content as bytes
        """
        pass

    @abstractmethod
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from blob storage.

        Args:
            object_name: Name/key of the object to delete

        Returns:
            True if successful, False otherwise
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
