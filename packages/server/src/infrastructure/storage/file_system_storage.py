"""Local filesystem blob storage implementation."""

from pathlib import Path

from .storage import BlobStorage


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

    def _get_file_path(self, key: str) -> Path:
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
            raise ValueError(f"Invalid key: {key} - path traversal detected")

        return file_path

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload data to filesystem storage.

        Args:
            key: Unique identifier for the blob
            data: Binary data to store
            content_type: MIME type of the data

        Returns:
            str: File path to access the uploaded blob
        """
        file_path = self._get_file_path(key)

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write data to file
        with open(file_path, "wb") as f:
            f.write(data)

        return str(file_path)

    def download(self, key: str) -> bytes:
        """
        Download data from filesystem storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bytes: Binary data from storage

        Raises:
            FileNotFoundError: If blob doesn't exist
        """
        file_path = self._get_file_path(key)

        if not file_path.exists():
            raise FileNotFoundError(f"Blob {key} not found")

        with open(file_path, "rb") as f:
            return f.read()

    def delete(self, key: str) -> bool:
        """
        Delete a blob from filesystem storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        file_path = self._get_file_path(key)

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
        file_path = self._get_file_path(key)
        return file_path.exists() and file_path.is_file()

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get a file path URL for accessing the blob.

        Args:
            key: Unique identifier for the blob
            expires_in: URL expiration time in seconds (ignored for filesystem)

        Returns:
            str: File path URL for blob access
        """
        file_path = self._get_file_path(key)
        return f"file://{file_path}"
