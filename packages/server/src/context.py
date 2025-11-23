"""Application context for dependency injection."""

from shared.database.sql import PostgresSQLDatabase, SqlDatabase
from shared.llm import LlmProvider, create_llm_provider
from shared.messaging import RabbitMQPublisher
from shared.repositories import (
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlUserRepository,
    SqlWorkspaceRepository,
)
from shared.storage import BlobStorage, FileSystemBlobStorage, S3BlobStorage

from src import config
from src.domains.chat.service import ChatService
from src.domains.documents.service import DocumentService
from src.domains.users.service import UserService
from src.domains.workspaces.service import WorkspaceService


def create_database() -> SqlDatabase:
    """Create database instance from config."""
    return PostgresSQLDatabase(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        database=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
    )


def create_blob_storage() -> BlobStorage:
    """Create blob storage instance from config."""
    if config.BLOB_STORAGE_TYPE == "s3":
        return S3BlobStorage(
            endpoint=config.S3_ENDPOINT_URL,
            access_key=config.S3_ACCESS_KEY,
            secret_key=config.S3_SECRET_KEY,
            bucket_name=config.S3_BUCKET_NAME,
            secure=False,
        )
    else:
        return FileSystemBlobStorage(base_path=config.FILE_SYSTEM_STORAGE_PATH)


def create_llm() -> LlmProvider:
    """Create LLM provider instance from config."""
    provider_type = config.LLM_PROVIDER

    if provider_type == "ollama":
        return create_llm_provider(
            provider_type="ollama",
            base_url=config.OLLAMA_BASE_URL,
            model_name=config.OLLAMA_LLM_MODEL,
        )
    elif provider_type == "openai":
        return create_llm_provider(
            provider_type="openai",
            api_key=config.OPENAI_API_KEY,
            model_name=config.OPENAI_MODEL,
        )
    elif provider_type == "claude":
        return create_llm_provider(
            provider_type="claude",
            api_key=config.ANTHROPIC_API_KEY,
            model_name=config.ANTHROPIC_MODEL,
        )
    elif provider_type == "huggingface":
        return create_llm_provider(
            provider_type="huggingface",
            api_key=config.HUGGINGFACE_API_KEY,
            model_name=config.HUGGINGFACE_MODEL,
        )
    else:
        # Default to ollama
        return create_llm_provider(
            provider_type="ollama",
            base_url=config.OLLAMA_BASE_URL,
            model_name=config.OLLAMA_LLM_MODEL,
        )


def create_message_publisher() -> RabbitMQPublisher | None:
    """Create message publisher from config (None if not configured)."""
    # RabbitMQ is optional - return None if not configured
    # Add RabbitMQ config to config.py when needed
    return None


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
            message_publisher if message_publisher is not None else create_message_publisher()
        )

        # Initialize LLM provider
        self.llm_provider = create_llm()

        # Create repositories using shared library SQL implementations
        user_repo = SqlUserRepository(db)
        document_repo = SqlDocumentRepository(db)
        session_repo = SqlChatSessionRepository(db)
        message_repo = SqlChatMessageRepository(db)
        workspace_repo = SqlWorkspaceRepository(db)

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
        self.workspace_service = WorkspaceService(workspace_repo=workspace_repo)


def create_app_context(db: SqlDatabase) -> AppContext:
    """
    Factory function to create application context.

    Args:
        db: SqlDatabase instance

    Returns:
        AppContext: Application context with all services initialized
    """
    return AppContext(db)
