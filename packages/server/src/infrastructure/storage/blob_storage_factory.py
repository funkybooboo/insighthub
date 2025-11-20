"""Factory for creating blob storage instances."""

from enum import Enum

from shared.storage import BlobStorage
from shared.storage.file_system_blob_storage import FileSystemBlobStorage
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage
from shared.storage.minio_storage import MinIOBlobStorage

from src import config


class BlobStorageType(Enum):
    """Enum for blob storage implementation types."""

    S3 = "s3"
    FILE_SYSTEM = "file_system"
    IN_MEMORY = "in_memory"


def create_blob_storage(storage_type: BlobStorageType | None = None) -> BlobStorage:
    """
    Create a blob storage instance based on environment configuration.

    Args:
        storage_type: Type of blob storage implementation to use.
                     If None, reads from config.BLOB_STORAGE_TYPE.

    Returns:
        BlobStorage: Configured blob storage instance

    Raises:
        ValueError: If storage_type is not supported
    """
    if storage_type is None:
        storage_type = BlobStorageType(config.BLOB_STORAGE_TYPE)

    if storage_type == BlobStorageType.S3:
        return MinIOBlobStorage(
            endpoint=config.S3_ENDPOINT_URL,
            access_key=config.S3_ACCESS_KEY,
            secret_key=config.S3_SECRET_KEY,
            bucket_name=config.S3_BUCKET_NAME,
        )
    elif storage_type == BlobStorageType.FILE_SYSTEM:
        return FileSystemBlobStorage(base_path=config.FILE_SYSTEM_STORAGE_PATH)
    elif storage_type == BlobStorageType.IN_MEMORY:
        return InMemoryBlobStorage()
    else:
        raise ValueError(f"Unsupported blob storage type: {storage_type}")
