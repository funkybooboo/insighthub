"""File system blob storage implementation."""

import hashlib
import shutil
from pathlib import Path
from typing import BinaryIO

from .interface import BlobStorage


class FileSystemBlobStorage(BlobStorage):
    """File system blob storage implementation."""

    def __init__(self, base_path: str) -> None:
        """
        Initialize file system storage.

        Args:
            base_path: Base directory path for storing files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, object_name: str) -> Path:
        """
        Get full file path for an object name.

        Args:
            object_name: Name/key of the object

        Returns:
            Path: Full path to the file
        """
        full_path = self.base_path / object_name
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> str:
        """
        Upload a file to file system storage.

        Args:
            file_obj: File-like object to upload
            object_name: Name/key for the object

        Returns:
            str: Object name/key
        """
        full_path = self._get_full_path(object_name)
        file_obj.seek(0)

        with open(full_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)

        return object_name

    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from file system storage.

        Args:
            object_name: Name/key of the object to download

        Returns:
            bytes: File content

        Raises:
            FileNotFoundError: If file not found
        """
        full_path = self._get_full_path(object_name)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {object_name}")

        with open(full_path, "rb") as f:
            return f.read()

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from file system storage.

        Args:
            object_name: Name/key of the object to delete

        Returns:
            bool: True if deletion was successful
        """
        full_path = self._get_full_path(object_name)

        if full_path.exists():
            full_path.unlink()

            # Clean up empty parent directories
            try:
                parent = full_path.parent
                while parent != self.base_path and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
            except OSError:
                pass

            return True
        return False

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in file system storage.

        Args:
            object_name: Name/key of the object to check

        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = self._get_full_path(object_name)
        return full_path.exists()

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
