"""In-memory blob storage implementation for testing."""

import hashlib
from typing import BinaryIO

from .interface import BlobStorage


class InMemoryBlobStorage(BlobStorage):
    """In-memory blob storage implementation for unit testing."""

    def __init__(self) -> None:
        """Initialize in-memory storage."""
        self.storage: dict[str, bytes] = {}

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> str:
        """
        Upload a file to in-memory storage.

        Args:
            file_obj: File-like object to upload
            object_name: Name/key for the object

        Returns:
            str: Object name/key
        """
        file_obj.seek(0)
        self.storage[object_name] = file_obj.read()
        return object_name

    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from in-memory storage.

        Args:
            object_name: Name/key of the object to download

        Returns:
            bytes: File content

        Raises:
            Exception: If file not found
        """
        if object_name not in self.storage:
            raise Exception(f"File not found: {object_name}")
        return self.storage[object_name]

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from in-memory storage.

        Args:
            object_name: Name/key of the object to delete

        Returns:
            bool: True if deletion was successful
        """
        if object_name in self.storage:
            del self.storage[object_name]
            return True
        return False

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in in-memory storage.

        Args:
            object_name: Name/key of the object to check

        Returns:
            bool: True if file exists, False otherwise
        """
        return object_name in self.storage

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_obj: File-like object

        Returns:
            str: SHA-256 hash hex digest
        """
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        file_obj.seek(0)
        return sha256_hash.hexdigest()
