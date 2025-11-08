"""Test context for dependency injection in tests."""

from sqlalchemy.orm import Session
from src.domains.chat.repositories import ChatMessageRepository, ChatSessionRepository
from src.domains.chat.service import ChatService
from src.domains.documents.repositories import DocumentRepository
from src.domains.documents.service import DocumentService
from src.domains.users.repositories import UserRepository
from src.domains.users.service import UserService
from src.infrastructure.factories import (
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)
from src.infrastructure.storage import BlobStorage, InMemoryBlobStorage


class UnitTestContext:
    """Test context for unit tests using in-memory implementations.

    This context always uses in-memory implementations (SQLite, InMemoryBlobStorage)
    for fast, isolated unit tests that don't require external dependencies.
    """

    def __init__(self, db: Session):
        """
        Initialize unit test context with dependencies.

        Args:
            db: Database session (should be SQLite in-memory)
        """
        self.db = db

        # Always use in-memory blob storage for unit tests
        self.blob_storage: BlobStorage = InMemoryBlobStorage()

        # Initialize repositories
        self.user_repository: UserRepository = create_user_repository(db)
        self.document_repository: DocumentRepository = create_document_repository(db)
        self.chat_session_repository: ChatSessionRepository = create_chat_session_repository(db)
        self.chat_message_repository: ChatMessageRepository = create_chat_message_repository(db)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=self.user_repository)
        self.document_service = DocumentService(
            repository=self.document_repository,
            blob_storage=self.blob_storage,
        )
        self.chat_service = ChatService(
            session_repository=self.chat_session_repository,
            message_repository=self.chat_message_repository,
        )


class IntegrationTestContext:
    """Test context for integration tests using real implementations.

    This context uses real implementations (PostgreSQL via testcontainers,
    MinIO via testcontainers) for integration tests that verify component
    interactions with real databases.
    """

    def __init__(self, db: Session, blob_storage: BlobStorage):
        """
        Initialize integration test context with dependencies.

        Args:
            db: Database session (should be PostgreSQL from testcontainer)
            blob_storage: Blob storage instance (should be MinIO from testcontainer)
        """
        self.db = db
        self.blob_storage = blob_storage

        # Initialize repositories
        self.user_repository: UserRepository = create_user_repository(db)
        self.document_repository: DocumentRepository = create_document_repository(db)
        self.chat_session_repository: ChatSessionRepository = create_chat_session_repository(db)
        self.chat_message_repository: ChatMessageRepository = create_chat_message_repository(db)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=self.user_repository)
        self.document_service = DocumentService(
            repository=self.document_repository,
            blob_storage=self.blob_storage,
        )
        self.chat_service = ChatService(
            session_repository=self.chat_session_repository,
            message_repository=self.chat_message_repository,
        )


def create_unit_test_context(db: Session) -> UnitTestContext:
    """
    Factory function to create unit test context.

    Args:
        db: Database session (should be SQLite in-memory)

    Returns:
        UnitTestContext: Test context with in-memory implementations
    """
    return UnitTestContext(db=db)


def create_integration_test_context(
    db: Session,
    blob_storage: BlobStorage,
) -> IntegrationTestContext:
    """
    Factory function to create integration test context.

    Args:
        db: Database session (should be PostgreSQL from testcontainer)
        blob_storage: Blob storage instance (should be MinIO from testcontainer)

    Returns:
        IntegrationTestContext: Test context with real implementations
    """
    return IntegrationTestContext(db=db, blob_storage=blob_storage)
