"""Factory for creating blob storage instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .blob_storage import BlobStorage
from .file_system_blob_storage import FileSystemBlobStorage
from .in_memory_blob_storage import InMemoryBlobStorage
from .s3_blob_storage import S3BlobStorage


class BlobStorageType(Enum):
    """Enum for blob storage implementation types."""

    S3 = "s3"
    FILE_SYSTEM = "file_system"
    IN_MEMORY = "in_memory"


def create_blob_storage(
    storage_type: str,
    endpoint: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
    bucket_name: str | None = None,
    secure: bool = False,
    base_path: str | None = None,
) -> Option[BlobStorage]:
    """
    Create a blob storage instance based on configuration.

    Args:
        storage_type: Type of blob storage ("s3", "file_system", "in_memory")
        endpoint: S3 endpoint (required for s3)
        access_key: S3 access key (required for s3)
        secret_key: S3 secret key (required for s3)
        bucket_name: S3 bucket name (required for s3)
        secure: Use HTTPS for S3 (default False)
        base_path: File system base path (required for file_system)

    Returns:
        Some(BlobStorage) if creation succeeds, Nothing() if type unknown or params missing
    """
    try:
        storage_enum = BlobStorageType(storage_type)
    except ValueError:
        return Nothing()

    if storage_enum == BlobStorageType.S3:
        if (
            endpoint is None
            or access_key is None
            or secret_key is None
            or bucket_name is None
        ):
            return Nothing()
        return Some(
            S3BlobStorage(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                bucket_name=bucket_name,
                secure=secure,
            )
        )
    elif storage_enum == BlobStorageType.FILE_SYSTEM:
        if not base_path:
            return Nothing()
        return Some(FileSystemBlobStorage(base_path=base_path))
    elif storage_enum == BlobStorageType.IN_MEMORY:
        return Some(InMemoryBlobStorage())

    return Nothing()
