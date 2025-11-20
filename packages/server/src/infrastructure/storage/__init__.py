"""Blob storage module - server factory wrapping shared implementations."""

from shared.storage import BlobStorage

from .blob_storage_factory import BlobStorageType, create_blob_storage

__all__ = [
    "BlobStorage",
    "BlobStorageType",
    "create_blob_storage",
]
