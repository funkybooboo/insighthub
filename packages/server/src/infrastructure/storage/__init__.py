"""Storage infrastructure for file operations."""

from .file_system_storage import FileSystemBlobStorage
from .storage import BlobStorage

try:
    from .s3_storage import S3BlobStorage

    S3_AVAILABLE = True
except ImportError:
    S3BlobStorage = None
    S3_AVAILABLE = False

__all__ = [
    "BlobStorage",
    "FileSystemBlobStorage",
    "S3_AVAILABLE",
]

if S3_AVAILABLE:
    __all__.append("S3BlobStorage")
