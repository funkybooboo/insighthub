"""Factory for creating DocumentService instances."""

from enum import Enum

from sqlalchemy.orm import Session

from src import config
from src.blob_storages import BlobStorage, create_blob_storage
from src.repositories import create_document_repository

from .default_document_service import DefaultDocumentService
from .document_service import DocumentService


class DocumentServiceType(Enum):
    """Enum for document service implementation types."""

    DEFAULT = "default"


def create_document_service(
    db: Session,
    blob_storage: BlobStorage | None = None,
    service_type: DocumentServiceType | None = None,
) -> DocumentService:
    """
    Create a DocumentService instance with dependencies.

    Args:
        db: Database session
        blob_storage: Optional blob storage instance (creates one if not provided)
        service_type: Type of document service implementation to use.
                     If None, reads from config.DOCUMENT_SERVICE_TYPE.

    Returns:
        DocumentService: Service instance with injected dependencies

    Raises:
        ValueError: If service_type is not supported
    """
    if service_type is None:
        service_type = DocumentServiceType(config.DOCUMENT_SERVICE_TYPE)

    repository = create_document_repository(db)
    if blob_storage is None:
        blob_storage = create_blob_storage()

    if service_type == DocumentServiceType.DEFAULT:
        return DefaultDocumentService(repository=repository, blob_storage=blob_storage)
    else:
        raise ValueError(f"Unsupported document service type: {service_type}")
