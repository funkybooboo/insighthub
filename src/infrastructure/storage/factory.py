"""Factory for creating blob storage instances."""

from .file_system_storage import FileSystemBlobStorage
from .s3_storage import S3BlobStorage
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
        return FileSystemBlobStorage(base_path=base_path)
    elif storage_type == "s3":
        endpoint = kwargs.get("endpoint")
        access_key = kwargs.get("access_key")
        secret_key = kwargs.get("secret_key")
        bucket_name = kwargs.get("bucket_name", "document")
        secure = kwargs.get("secure", True)
        region = kwargs.get("region")

        if not endpoint or not access_key or not secret_key:
            raise ValueError("S3 storage requires endpoint, access_key, and secret_key")

        # Strip protocol from endpoint if present (MinIO expects host:port only)
        if endpoint.startswith("https://"):
            endpoint = endpoint[8:]
            secure = True
        elif endpoint.startswith("http://"):
            endpoint = endpoint[7:]
            secure = False

        return S3BlobStorage(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            secure=secure,
            region=region,
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
