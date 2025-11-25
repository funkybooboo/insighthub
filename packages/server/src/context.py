"""Application context for dependency injection."""

from shared.database.sql import PostgresSqlDatabase, SqlDatabase
from shared.database.vector import create_vector_database
from shared.documents.embedding import create_embedding_encoder
from shared.llm import LlmProvider, create_llm_provider
from shared.messaging import RabbitMQPublisher
from shared.orchestrators import VectorRAG
from shared.repositories import (
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDefaultRagConfigRepository,
    SqlDocumentRepository,
    SqlRagConfigRepository,
    SqlUserRepository,
    SqlWorkspaceRepository,
)
from shared.storage import BlobStorage, FileSystemBlobStorage, S3BlobStorage

from src import config
from src.domains.workspaces.chat.service import ChatService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.rag_config.service import RagConfigService
from src.domains.auth.service import UserService
from shared.repositories import UserRepository
from src.domains.workspaces.service import WorkspaceService


def create_database() -> SqlDatabase:
    """Create database instance from config."""
    return PostgresSqlDatabase(
        db_url=config.DATABASE_URL,
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
    if not config.RABBITMQ_HOST:
        return None

    try:
        publisher = RabbitMQPublisher(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            username=config.RABBITMQ_USER,
            password=config.RABBITMQ_PASS,
            exchange=config.RABBITMQ_EXCHANGE,
            exchange_type=config.RABBITMQ_EXCHANGE_TYPE,
        )
        publisher.connect()
        return publisher
    except Exception:
        # RabbitMQ connection failed - continue without messaging
        return None


def create_rag_system():
    """Create RAG system components from config."""
    try:
        # Create vector database
        vector_db = create_vector_database(
            db_type="qdrant",
            url=f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}",
            collection_name=config.QDRANT_COLLECTION_NAME,
            vector_size=768,  # Default embedding dimension
        )

        if not vector_db:
            return None

        # Create embedding encoder
        embedder = create_embedding_encoder(
            encoder_type="ollama",
            model=config.OLLAMA_EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL,
        )

        if not embedder:
            return None

        # Create VectorRAG orchestrator
        rag = VectorRAG(embedder=embedder, vector_store=vector_db)
        return rag

    except Exception:
        # RAG system creation failed - continue without RAG
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

        # Initialize RAG system (optional)
        self.rag_system = create_rag_system()

        # Create repositories using server implementations
        user_repo = UserRepository(db)
        document_repo = SqlDocumentRepository(db)
        session_repo = SqlChatSessionRepository(db)
        message_repo = SqlChatMessageRepository(db)
        workspace_repo = SqlWorkspaceRepository(db)
        default_rag_config_repo = SqlDefaultRagConfigRepository(db)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=user_repo)
        self.document_service = DocumentService(
            repository=document_repo,
            blob_storage=self.blob_storage,
            message_publisher=self.message_publisher,
        )
        self.chat_service = ChatService(
            session_repository=session_repo,
            message_repository=message_repo,
            rag_system=self.rag_system,
            message_publisher=self.message_publisher
        )
        self.workspace_service = WorkspaceService(
            workspace_repo=workspace_repo,
            message_publisher=self.message_publisher,
        )

        # Initialize RAG config repository and service
        rag_config_repo = SqlRagConfigRepository(db)
        self.rag_config_service = RagConfigService(rag_config_repo, self.workspace_service)

        # Initialize repositories
        self.default_rag_config_repository = default_rag_config_repo


def create_app_context(db: SqlDatabase) -> AppContext:
    """
    Factory function to create application context.

    Args:
        db: SqlDatabase instance

    Returns:
        AppContext: Application context with all services initialized
    """
    return AppContext(db)
