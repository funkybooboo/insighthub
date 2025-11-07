"""Application context for dependency injection."""

from sqlalchemy.orm import Session

from src.blob_storages import BlobStorage, create_blob_storage
from src.services import (
    ChatService,
    DocumentService,
    UserService,
    create_chat_service,
    create_document_service,
    create_user_service,
)


class AppContext:
    """Application context that holds service implementations."""

    def __init__(self, db: Session, blob_storage: BlobStorage | None = None):
        """
        Initialize application context with dependencies.

        Args:
            db: Database session
            blob_storage: Optional blob storage instance (creates one if not provided)
        """
        self.db = db

        # Initialize blob storage
        self.blob_storage = blob_storage if blob_storage is not None else create_blob_storage()

        # Initialize services with dependency injection
        self.user_service: UserService = create_user_service(db)
        self.document_service: DocumentService = create_document_service(db, self.blob_storage)
        self.chat_service: ChatService = create_chat_service(db)


def create_app_context(db: Session) -> AppContext:
    """
    Factory function to create application context.

    Args:
        db: Database session

    Returns:
        AppContext: Application context with all services initialized
    """
    return AppContext(db)
