"""Test context for dependency injection in tests."""

from sqlalchemy.orm import Session

from src.blob_storages import BlobStorage, InMemoryBlobStorage
from src.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)
from src.services import (
    ChatService,
    DocumentService,
    UserService,
    create_chat_service,
    create_document_service,
    create_user_service,
)


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
        self.user_service: UserService = create_user_service(db)
        self.document_service: DocumentService = create_document_service(db, self.blob_storage)
        self.chat_service: ChatService = create_chat_service(db)


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
        self.user_service: UserService = create_user_service(db)
        self.document_service: DocumentService = create_document_service(db, self.blob_storage)
        self.chat_service: ChatService = create_chat_service(db)


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
