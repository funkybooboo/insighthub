"""Factory for creating blob storage instances using server configuration."""

from shared.storage import BlobStorage, FileSystemBlobStorage, S3BlobStorage

from src import config


def create_blob_storage() -> BlobStorage:
    """
    Create a blob storage instance based on server configuration.

    Uses BLOB_STORAGE_TYPE environment variable to determine which storage to use.
    Supported types: s3, file_system

    Returns:
        BlobStorage instance configured based on environment variables
    """
    storage_type = config.BLOB_STORAGE_TYPE

    if storage_type == "s3":
        return S3BlobStorage(
            endpoint=config.S3_ENDPOINT_URL,
            access_key=config.S3_ACCESS_KEY,
            secret_key=config.S3_SECRET_KEY,
            bucket_name=config.S3_BUCKET_NAME,
            secure=False,
        )
    else:
        # Default to file system storage
        return FileSystemBlobStorage(base_path=config.FILE_SYSTEM_STORAGE_PATH)
