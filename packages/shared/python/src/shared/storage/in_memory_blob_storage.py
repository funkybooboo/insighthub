"""In-memory blob storage implementation for testing."""

import hashlib
from typing import BinaryIO

from shared.types.result import Err, Ok, Result

from .blob_storage import BlobStorage, BlobStorageError


class InMemoryBlobStorage(BlobStorage):
    """In-memory blob storage implementation for unit testing."""

    def __init__(self) -> None:
        """Initialize in-memory storage."""
        self._storage: dict[str, bytes] = {}

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> Result[str, BlobStorageError]:
        """Upload a file to in-memory storage."""
        file_obj.seek(0)
        self._storage[object_name] = file_obj.read()
        return Ok(object_name)

    def download_file(self, object_name: str) -> Result[bytes, BlobStorageError]:
        """Download a file from in-memory storage."""
        if object_name not in self._storage:
            return Err(BlobStorageError(f"File not found: {object_name}", code="NOT_FOUND"))
        return Ok(self._storage[object_name])

    def delete_file(self, object_name: str) -> Result[bool, BlobStorageError]:
        """Delete a file from in-memory storage."""
        if object_name in self._storage:
            del self._storage[object_name]
            return Ok(True)
        return Ok(False)

    def file_exists(self, object_name: str) -> bool:
        """Check if a file exists in in-memory storage."""
        return object_name in self._storage

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        file_obj.seek(0)
        return sha256_hash.hexdigest()

    def list_files(self, prefix: str | None = None) -> list[str]:
        """List all files with optional prefix filter."""
        if prefix:
            return [key for key in self._storage if key.startswith(prefix)]
        return list(self._storage.keys())
