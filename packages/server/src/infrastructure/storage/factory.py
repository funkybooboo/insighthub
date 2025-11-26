"""Factory for creating blob storage instances."""

from .file_system_storage import FileSystemStorage
from .storage import BlobStorage


def create_blob_storage(storage_type: str = "filesystem", **kwargs) -> BlobStorage:
    """Create a blob storage instance based on configuration.

    Args:
        storage_type: Type of storage ("filesystem", "s3")
        **kwargs: Additional configuration parameters

    Returns:
        BlobStorage instance

    Raises:
        ValueError: If storage_type is not supported
    """
    if storage_type == "filesystem":
        base_path = kwargs.get("base_path", "./uploads")
        return FileSystemStorage(base_path=base_path)
    elif storage_type == "s3":
        # TODO: Implement S3 storage
        raise NotImplementedError("S3 storage not yet implemented")
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
