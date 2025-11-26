"""Storage infrastructure for file operations."""

from .storage import BlobStorage
from .file_system_storage import FileSystemBlobStorage

try:
    from .s3_storage import S3BlobStorage
    S3_AVAILABLE = True
except ImportError:
    S3BlobStorage = None
    S3_AVAILABLE = False

__all__ = [
    "BlobStorage",
    "FileSystemBlobStorage",
    "S3BlobStorage",
    "S3_AVAILABLE",
]