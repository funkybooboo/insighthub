"""Application context for dependency injection."""

from sqlalchemy.orm import Session

from src.domains.chat.service import ChatService
from src.domains.documents.service import DocumentService
from src.domains.users.service import UserService
from src.infrastructure.factories import (
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)
from src.infrastructure.storage import BlobStorage, create_blob_storage


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

        # Create repositories
        user_repo = create_user_repository(db)
        document_repo = create_document_repository(db)
        session_repo = create_chat_session_repository(db)
        message_repo = create_chat_message_repository(db)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=user_repo)
        self.document_service = DocumentService(
            repository=document_repo, blob_storage=self.blob_storage
        )
        self.chat_service = ChatService(
            session_repository=session_repo, message_repository=message_repo
        )


def create_app_context(db: Session) -> AppContext:
    """
    Factory function to create application context.

    Args:
        db: Database session

    Returns:
        AppContext: Application context with all services initialized
    """
    return AppContext(db)
