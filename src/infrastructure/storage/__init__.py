"""Storage infrastructure for file operations."""

from returns.result import Result

from src.infrastructure.types.errors import StorageError

from .file_system_storage import FileSystemBlobStorage
from .storage import BlobStorage

try:
    from .s3_storage import S3BlobStorage

    S3_AVAILABLE = True
except ImportError:
    # Create a placeholder class that raises an error if instantiated
    class S3BlobStorage(BlobStorage):  # type: ignore[no-redef]
        """Placeholder when boto3 is not installed."""

        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise ImportError("boto3 is required for S3BlobStorage")

        def upload(
            self, key: str, data: bytes, content_type: str = "application/octet-stream"
        ) -> Result[str, StorageError]:
            raise NotImplementedError

        def download(self, key: str) -> Result[bytes, StorageError]:
            raise NotImplementedError

        def delete(self, key: str) -> bool:
            raise NotImplementedError

        def exists(self, key: str) -> bool:
            raise NotImplementedError

    S3_AVAILABLE = False

__all__ = [
    "BlobStorage",
    "FileSystemBlobStorage",
    "S3_AVAILABLE",
]

if S3_AVAILABLE:
    __all__.append("S3BlobStorage")
