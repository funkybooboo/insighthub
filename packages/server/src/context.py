"""Application context for dependency injection."""

from shared.database.sql import SqlDatabase
from shared.messaging import RabbitMQPublisher
from shared.storage import BlobStorage

from src.domains.chat.service import ChatService
from src.domains.documents.service import DocumentService
from src.domains.users.service import UserService
from src.infrastructure.factories import (
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)
from src.infrastructure.llm import create_llm_provider
from src.infrastructure.messaging import create_rabbitmq_publisher
from src.infrastructure.storage import create_blob_storage


class AppContext:
    """Application context that holds service implementations."""

    def __init__(
        self,
        db: SqlDatabase,
        blob_storage: BlobStorage | None = None,
        message_publisher: RabbitMQPublisher | None = None,
    ):
        """
        Initialize application context with dependencies.

        Args:
            db: SqlDatabase instance
            blob_storage: Optional blob storage instance (creates one if not provided)
            message_publisher: Optional RabbitMQ publisher (creates one if not provided)
        """
        self.db = db

        # Initialize blob storage
        self.blob_storage = blob_storage if blob_storage is not None else create_blob_storage()

        # Initialize RabbitMQ publisher (None if disabled)
        self.message_publisher = (
            message_publisher if message_publisher is not None else create_rabbitmq_publisher()
        )

        # Initialize LLM provider using factory
        self.llm_provider = create_llm_provider()

        # Create repositories
        user_repo = create_user_repository(db)
        document_repo = create_document_repository(db)
        session_repo = create_chat_session_repository(db)
        message_repo = create_chat_message_repository(db)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=user_repo)
        self.document_service = DocumentService(
            repository=document_repo,
            blob_storage=self.blob_storage,
            message_publisher=self.message_publisher,
        )
        self.chat_service = ChatService(
            session_repository=session_repo, message_repository=message_repo
        )


def create_app_context(db: SqlDatabase) -> AppContext:
    """
    Factory function to create application context.

    Args:
        db: SqlDatabase instance

    Returns:
        AppContext: Application context with all services initialized
    """
    return AppContext(db)
