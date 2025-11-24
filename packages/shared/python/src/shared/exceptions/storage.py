"""Exceptions specific to the storage module."""

from shared.exceptions.base import DomainException


class StorageException(DomainException):
    """Base exception for all storage-related errors."""

    def __init__(self, message: str, status_code: int = 500):
        """Initialize storage exception."""
        super().__init__(f"Storage Error: {message}", status_code)


class BlobStorageError(StorageException):
    """Raised for errors related to blob storage."""

    def __init__(self, message: str):
        """Initialize blob storage error."""
        super().__init__(f"Blob storage operation failed: {message}", status_code=500)


class FileSystemError(StorageException):
    """Raised for errors related to the file system."""

    def __init__(self, message: str):
        """Initialize file system error."""
        super().__init__(f"File system operation failed: {message}", status_code=500)
