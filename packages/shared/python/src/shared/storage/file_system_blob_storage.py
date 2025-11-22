"""File system blob storage implementation."""

import hashlib
import shutil
from pathlib import Path
from typing import BinaryIO

from shared.types.result import Err, Ok, Result

from .blob_storage import BlobStorage, BlobStorageError


class FileSystemBlobStorage(BlobStorage):
    """File system blob storage implementation."""

    def __init__(self, base_path: str) -> None:
        """
        Initialize file system storage.

        Args:
            base_path: Base directory path for storing files
        """
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, object_name: str) -> Path:
        """Get full file path for an object name."""
        full_path = self._base_path / object_name
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> Result[str, BlobStorageError]:
        """Upload a file to file system storage."""
        try:
            full_path = self._get_full_path(object_name)
            file_obj.seek(0)

            with open(full_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)

            return Ok(object_name)
        except OSError as e:
            return Err(BlobStorageError(f"Upload failed: {e}", code="UPLOAD_ERROR"))

    def download_file(self, object_name: str) -> Result[bytes, BlobStorageError]:
        """Download a file from file system storage."""
        full_path = self._get_full_path(object_name)

        if not full_path.exists():
            return Err(BlobStorageError(f"File not found: {object_name}", code="NOT_FOUND"))

        try:
            with open(full_path, "rb") as f:
                return Ok(f.read())
        except OSError as e:
            return Err(BlobStorageError(f"Download failed: {e}", code="DOWNLOAD_ERROR"))

    def delete_file(self, object_name: str) -> Result[bool, BlobStorageError]:
        """Delete a file from file system storage."""
        full_path = self._get_full_path(object_name)

        if not full_path.exists():
            return Ok(False)

        try:
            full_path.unlink()

            try:
                parent = full_path.parent
                while parent != self._base_path and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
            except OSError:
                pass

            return Ok(True)
        except OSError as e:
            return Err(BlobStorageError(f"Delete failed: {e}", code="DELETE_ERROR"))

    def file_exists(self, object_name: str) -> bool:
        """Check if a file exists in file system storage."""
        full_path = self._get_full_path(object_name)
        return full_path.exists()

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        file_obj.seek(0)
        return sha256_hash.hexdigest()
