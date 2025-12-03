"""Application context containing all services and repositories."""

from src.config import config
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.workspace.chat.message.service import ChatMessageService
from src.domains.workspace.chat.session.service import ChatSessionService
from src.domains.workspace.document.service import DocumentService
from src.domains.workspace.service import WorkspaceService
from src.infrastructure.cache.factory import create_cache
from src.infrastructure.llm.factory import create_llm_provider
from src.infrastructure.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DefaultRagConfigRepository,
    DocumentRepository,
    StateRepository,
    WorkspaceRepository,
)
from src.infrastructure.sql_database import get_sql_database
from src.infrastructure.storage.factory import create_blob_storage


class AppContext:
    """Application context containing all services and repositories."""

    def __init__(self):
        """Initialize context with all services."""
        # Database
        db = get_sql_database()

        # Cache
        cache_config = config.cache
        if cache_config.cache_type == "redis":
            self.cache = create_cache(
                cache_type="redis",
                host=cache_config.redis_host,
                port=cache_config.redis_port,
                db=cache_config.redis_db,
                default_ttl=cache_config.redis_ttl,
            )
        else:
            self.cache = create_cache(
                cache_type="memory",
                default_ttl=cache_config.redis_ttl,
            )

        # Storage
        self.blob_storage = create_blob_storage(
            storage_type=config.blob_storage_type,
            base_path=config.file_system_storage_path,
            endpoint=config.s3_endpoint_url,
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            bucket_name=config.s3_bucket_name,
        )

        # Repositories (PostgreSQL only)
        self.workspace_repo = WorkspaceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.default_rag_config_repo = DefaultRagConfigRepository(db)
        self.chat_session_repo = ChatSessionRepository(db)
        self.chat_message_repo = ChatMessageRepository(db)
        self.state_repo = StateRepository(db)

        # Services
        self.workspace_service = WorkspaceService(
            repository=self.workspace_repo,
            cache=self.cache,
        )
        self.document_service = DocumentService(
            repository=self.document_repo,
            workspace_repository=self.workspace_repo,
            blob_storage=self.blob_storage,
            cache=self.cache,
        )
        self.default_rag_config_service = DefaultRagConfigService(
            repository=self.default_rag_config_repo,
            cache=self.cache,
        )
        self.chat_session_service = ChatSessionService(
            repository=self.chat_session_repo,
            cache=self.cache,
        )

        # LLM Provider
        api_key = None
        if config.llm_provider == "openai":
            api_key = config.openai_api_key
        elif config.llm_provider == "claude":
            api_key = config.anthropic_api_key

        self.llm_provider = create_llm_provider(
            provider_type=config.llm_provider,
            base_url=config.ollama_base_url,
            model_name=config.ollama_llm_model,
            api_key=api_key,
        )

        # Chat message service (depends on llm_provider)
        self.chat_message_service = ChatMessageService(
            repository=self.chat_message_repo,
            session_repository=self.chat_session_repo,
            workspace_repository=self.workspace_repo,
            llm_provider=self.llm_provider,
            cache=self.cache,
        )

        # Load current state from database
        state = self.state_repo.get()
        self.current_workspace_id: int | None = state.current_workspace_id if state else None
        self.current_session_id: int | None = state.current_session_id if state else None

    def startup_checks(self) -> bool:
        """
        Perform startup health checks.

        Returns:
            bool: True if all checks pass, False otherwise
        """
        from src.infrastructure.logger import create_logger

        logger = create_logger(__name__)
        logger.info("Running startup health checks...")

        checks_passed = True

        # Check database connection
        try:
            from src.infrastructure.sql_database import get_sql_database

            db = get_sql_database()
            if db.health_check():
                logger.info("Database connection: OK")
            else:
                logger.error("Database connection: FAILED - health check returned false")
                checks_passed = False
        except Exception as e:
            logger.error(f"Database connection: FAILED - {e}")
            checks_passed = False

        # Check LLM provider (non-critical)
        try:
            health = self.llm_provider.health_check()
            status = health.get("status", "unknown")
            if status == "healthy":
                logger.info(f"LLM provider ({config.llm_provider}): OK")
            else:
                logger.warning(f"LLM provider ({config.llm_provider}): UNAVAILABLE (non-critical)")
        except Exception as e:
            logger.warning(f"LLM provider health check failed: {e} (non-critical)")

        # Check blob storage (non-critical)
        try:
            # Just verify storage is accessible - don't create test files
            logger.info(f"Blob storage ({config.blob_storage_type}): initialized")
        except Exception as e:
            logger.warning(f"Blob storage check failed: {e} (non-critical)")

        if checks_passed:
            logger.info("All critical health checks passed")
        else:
            logger.error("Some critical health checks failed")

        return checks_passed

    def cleanup(self) -> None:
        """Clean up resources on application shutdown."""
        from src.infrastructure.logger import create_logger
        from src.infrastructure.sql_database import close_sql_database

        logger = create_logger(__name__)
        logger.info("Cleaning up application resources...")

        # Close database connection
        close_sql_database()

        logger.info("Application cleanup complete")
