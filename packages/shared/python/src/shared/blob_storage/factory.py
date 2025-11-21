"""
Factory for creating blob storage instances.

This factory can be used by server and workers to create the appropriate
blob storage implementation based on configuration.
"""

from enum import Enum
from typing import Optional

from .blob_storage import BlobStorage
from .file_system_blob_storage import FileSystemBlobStorage
from .in_memory_blob_storage import InMemoryBlobStorage
from .minio_storage import MinIOBlobStorage


class BlobStorageType(Enum):
    """Enum for blob storage implementation types."""

    S3 = "s3"
    FILE_SYSTEM = "file_system"
    IN_MEMORY = "in_memory"


def create_blob_storage(
    storage_type: str,
    endpoint_url: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket_name: Optional[str] = None,
    base_path: Optional[str] = None,
) -> BlobStorage:
    """
    Create a blob storage instance based on configuration.

    Args:
        storage_type: Type of blob storage ("s3", "file_system", "in_memory")
        endpoint_url: S3 endpoint URL (required for s3)
        access_key: S3 access key (required for s3)
        secret_key: S3 secret key (required for s3)
        bucket_name: S3 bucket name (required for s3)
        base_path: File system base path (required for file_system)

    Returns:
        BlobStorage: Configured blob storage instance

    Raises:
        ValueError: If storage_type is not supported or required params missing
    
    Examples:
        >>> # Create MinIO storage
        >>> storage = create_blob_storage(
        ...     storage_type="s3",
        ...     endpoint_url="http://localhost:9000",
        ...     access_key="minioadmin",
        ...     secret_key="minioadmin",
        ...     bucket_name="documents"
        ... )
        
        >>> # Create file system storage
        >>> storage = create_blob_storage(
        ...     storage_type="file_system",
        ...     base_path="/var/uploads"
        ... )
        
        >>> # Create in-memory storage (for testing)
        >>> storage = create_blob_storage(storage_type="in_memory")
    """
    storage_enum = BlobStorageType(storage_type)

    if storage_enum == BlobStorageType.S3:
        if not all([endpoint_url, access_key, secret_key, bucket_name]):
            raise ValueError(
                "S3 storage requires: endpoint_url, access_key, secret_key, bucket_name"
            )
        return MinIOBlobStorage(
            endpoint_url=endpoint_url,  # type: ignore
            access_key=access_key,  # type: ignore
            secret_key=secret_key,  # type: ignore
            bucket_name=bucket_name,  # type: ignore
        )
    elif storage_enum == BlobStorageType.FILE_SYSTEM:
        if not base_path:
            raise ValueError("File system storage requires: base_path")
        return FileSystemBlobStorage(base_path=base_path)
    elif storage_enum == BlobStorageType.IN_MEMORY:
        return InMemoryBlobStorage()
    else:
        raise ValueError(f"Unsupported blob storage type: {storage_type}")
