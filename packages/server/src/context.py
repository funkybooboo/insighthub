"""Application context for dependency injection."""

import contextlib
from typing import Any, cast

from shared.cache.factory import create_cache
from shared.database.sql import PostgresSqlDatabase, SqlDatabase
from shared.llm import LlmProvider, create_llm_provider
from shared.messaging import RabbitMQPublisher
from shared.repositories import (
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlWorkspaceRepository,
    create_user_repository,
)
from shared.storage import BlobStorage, FileSystemBlobStorage, S3BlobStorage

from src import config
from src.domains.auth.service import UserService
from src.domains.workspaces.chat.service import ChatService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.rag_config.service import RagConfigService
from src.domains.workspaces.service import WorkspaceService

# Try to import SqlDefaultRagConfigRepository, will be None if not available
SqlDefaultRagConfigRepository: Any = None
with contextlib.suppress(ImportError):
    from shared.repositories import SqlDefaultRagConfigRepository


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
    try:
        # Parse RabbitMQ URL to extract components
        from urllib.parse import urlparse

        parsed = urlparse(config.RABBITMQ_URL)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5672
        username = parsed.username or "guest"
        password = parsed.password or "guest"

        publisher = RabbitMQPublisher(
            host=host,
            port=port,
            username=username,
            password=password,
            exchange=config.RABBITMQ_EXCHANGE,
            exchange_type="topic",  # Default exchange type
        )
        publisher.connect()
        return publisher
    except Exception:
        # RabbitMQ connection failed - continue without messaging
        return None


def create_cache_instance() -> Any:
    """Create cache instance from config."""
    if not config.REDIS_URL:
        # Fall back to in-memory cache if Redis not configured
        return create_cache("in_memory", default_ttl=3600)  # 1 hour default TTL

    # Parse Redis URL
    # Expected format: redis://[:password@]host:port/db
    try:
        from urllib.parse import urlparse

        parsed = urlparse(config.REDIS_URL)

        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        db = int(parsed.path.lstrip("/")) if parsed.path and parsed.path != "/" else 0
        password = parsed.password

        return create_cache(
            "redis",
            host=host,
            port=port,
            db=db,
            password=password,
            default_ttl=3600,  # 1 hour default TTL
        )
    except Exception:
        # Redis configuration failed - fall back to in-memory
        return create_cache("in_memory", default_ttl=3600)


def create_rag_system_for_workspace(workspace_id: int, cache: Any = None) -> Any:
    """Create RAG system for a specific workspace based on its config."""
    try:
        # Get workspace to determine RAG type
        workspace = None
        if hasattr(cache, '_app_context') and cache._app_context:
            workspace_repo = cache._app_context.workspace_repository
            workspace = workspace_repo.get_by_id(workspace_id)

        if not workspace:
            return None

        # Get appropriate config based on workspace RAG type
        if workspace.rag_type == "vector" and workspace.vector_rag_config_id:
            vector_config_repo = cache._app_context.vector_rag_config_service.repository
            config = vector_config_repo.get_vector_rag_config(workspace_id)
            return _create_vector_rag_system(config, cache) if config else None

        elif workspace.rag_type == "graph" and workspace.graph_rag_config_id:
            graph_config_repo = cache._app_context.graph_rag_config_service.repository
            config = graph_config_repo.get_graph_rag_config(workspace_id)
            return _create_graph_rag_system(config, cache) if config else None

        return None

    except Exception:
        # RAG system creation failed - continue without RAG
        return None


def create_rag_system(rag_config: Any, cache: Any = None) -> Any:
    """Create RAG system components from config (legacy support)."""
    try:
        if hasattr(rag_config, 'embedding_algorithm'):  # VectorRagConfig
            return _create_vector_rag_system(rag_config, cache)
        elif hasattr(rag_config, 'entity_extraction_algorithm'):  # GraphRagConfig
            return _create_graph_rag_system(rag_config, cache)
        else:
            # Legacy RagConfig - default to vector
            return _create_vector_rag_system(rag_config, cache)

    except Exception:
        # RAG system creation failed - continue without RAG
        return None


def _create_vector_rag_system(vector_config: Any, cache: Any = None) -> Any:
    """Create vector RAG system from config."""
    # Create vector store (high-level interface that works with Chunk objects)
    from shared.database.vector import create_vector_store

    vector_store = create_vector_store(
        db_type="qdrant",
        url=f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}",
        collection_name=config.QDRANT_COLLECTION_NAME,
        vector_size=768,  # Default embedding dimension
    )

    if not vector_store:
        raise RuntimeError("Failed to create vector store")

    # Create embedding encoder based on config
    from shared.documents.embedding import create_embedder_from_config

    embedder = create_embedder_from_config(
        embedding_algorithm=getattr(vector_config, 'embedding_algorithm', 'nomic-embed-text'),
        base_url=config.OLLAMA_BASE_URL
    )

    # Create chunker based on config
    from shared.documents.chunking import create_chunker_from_config

    chunker = create_chunker_from_config(
        chunking_algorithm=getattr(vector_config, 'chunking_algorithm', 'sentence'),
        chunk_size=getattr(vector_config, 'chunk_size', 1000),
        overlap=getattr(vector_config, 'chunk_overlap', 200)
    )

    # Create VectorRAG orchestrator
    try:
        from shared.orchestrators import VectorRAG

        rag = VectorRAG(embedder=embedder, vector_store=vector_store, cache=cache)
        return rag
    except ImportError:
        # VectorRAG not available
        return None


def _create_graph_rag_system(graph_config: Any, cache: Any = None) -> Any:
    """Create graph RAG system from config."""
    # TODO: Implement graph RAG system creation
    # This would create Neo4j graph database, entity/relationship extractors, etc.
    return None


class AppContext:
    """Application context that holds service implementations."""

    def __init__(
        self,
        db: SqlDatabase,
        blob_storage: BlobStorage | None = None,
        message_publisher: RabbitMQPublisher | None = None,
        cache: Any = None,
    ):
        """
        Initialize application context with dependencies.

        Args:
            db: SqlDatabase instance
            blob_storage: Optional blob storage instance (creates one if not provided)
            message_publisher: Optional RabbitMQ publisher (creates one if not provided)
            cache: Optional cache instance (creates one if not provided)
        """
        self.db = db

        # Initialize blob storage
        self.blob_storage = blob_storage if blob_storage is not None else create_blob_storage()

        # Initialize RabbitMQ publisher (None if disabled)
        self.message_publisher = (
            message_publisher if message_publisher is not None else create_message_publisher()
        )

        # Initialize cache
        self.cache = cache if cache is not None else create_cache_instance()

        # Initialize LLM provider
        self.llm_provider = create_llm()

        # Remove global RAG system - use workspace-specific systems instead
        self.rag_system = None

    def get_rag_system_for_workspace(self, workspace_id: int) -> Any:
        """Get RAG system for a specific workspace."""
        return create_rag_system_for_workspace(workspace_id, cache=self.cache)

        # Create repositories using server implementations
        postgres_db = cast(PostgresSqlDatabase, db)
        user_repo = create_user_repository("postgres", db_url=config.DATABASE_URL)
        if user_repo is None:
            raise ValueError("Failed to create user repository")
        document_repo = SqlDocumentRepository(postgres_db)
        session_repo = SqlChatSessionRepository(postgres_db)
        message_repo = SqlChatMessageRepository(postgres_db)
        self.workspace_repository = SqlWorkspaceRepository(postgres_db)
        if SqlDefaultRagConfigRepository is not None:
            default_rag_config_repo = SqlDefaultRagConfigRepository(postgres_db)
        else:
            default_rag_config_repo = None

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
            message_publisher=self.message_publisher,
            cache=self.cache,
        )
        # Initialize separate Vector and Graph RAG config services first
        from shared.repositories.vector_rag_config import SqlVectorRagConfigRepository
        from shared.repositories.graph_rag_config import SqlGraphRagConfigRepository
        from src.domains.workspaces.vector_rag_config_service import VectorRagConfigService
        from src.domains.workspaces.graph_rag_config_service import GraphRagConfigService

        vector_rag_config_repo = SqlVectorRagConfigRepository(postgres_db)
        graph_rag_config_repo = SqlGraphRagConfigRepository(postgres_db)

        self.vector_rag_config_service = VectorRagConfigService(vector_rag_config_repo, self.workspace_repository)
        self.graph_rag_config_service = GraphRagConfigService(graph_rag_config_repo, self.workspace_repository)

        self.workspace_service = WorkspaceService(
            workspace_repo=self.workspace_repository,
            vector_rag_config_service=self.vector_rag_config_service,
            graph_rag_config_service=self.graph_rag_config_service,
            message_publisher=self.message_publisher,
        )

        # Initialize RAG config services
        self.rag_config_service = RagConfigService(
            self.workspace_repository, self.workspace_service
        )

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
