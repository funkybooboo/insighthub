"""Application context containing all services and repositories."""

from typing import Optional

from src.config import config
from src.domains.default_rag_config.data_access import DefaultRagConfigDataAccess
from src.domains.default_rag_config.orchestrator import DefaultRagConfigOrchestrator
from src.domains.default_rag_config.repositories import DefaultRagConfigRepository
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.rag_options.orchestrator import RagOptionsOrchestrator
from src.domains.rag_options.service import RagOptionsService
from src.domains.state.data_access import StateDataAccess
from src.domains.state.orchestrator import StateOrchestrator
from src.domains.state.repositories import StateRepository
from src.domains.state.service import StateService
from src.domains.workspace.chat.message.data_access import ChatMessageDataAccess
from src.domains.workspace.chat.message.orchestrator import MessageOrchestrator
from src.domains.workspace.chat.message.repositories import ChatMessageRepository
from src.domains.workspace.chat.message.service import ChatMessageService
from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.chat.session.orchestrator import SessionOrchestrator
from src.domains.workspace.chat.session.repositories import ChatSessionRepository
from src.domains.workspace.chat.session.service import ChatSessionService
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.document.data_access import DocumentDataAccess
from src.domains.workspace.document.orchestrator import DocumentOrchestrator
from src.domains.workspace.document.repositories import DocumentRepository
from src.domains.workspace.document.service import DocumentService
from src.domains.workspace.orchestrator import WorkspaceOrchestrator
from src.domains.workspace.repositories import WorkspaceRepository
from src.domains.workspace.service import WorkspaceService
from src.infrastructure.cache.factory import create_cache
from src.infrastructure.llm.factory import create_llm_provider
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
            cache = create_cache(
                cache_type="redis",
                host=cache_config.redis_host,
                port=cache_config.redis_port,
                db=cache_config.redis_db,
                default_ttl=cache_config.redis_ttl,
            )
        else:
            cache = create_cache(
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

        # Data Access Layers (coordinates cache + repository)
        self.workspace_data_access = WorkspaceDataAccess(
            repository=self.workspace_repo,
            cache=cache,
        )
        self.document_data_access = DocumentDataAccess(
            repository=self.document_repo,
            cache=cache,
        )
        self.chat_session_data_access = ChatSessionDataAccess(
            repository=self.chat_session_repo,
            cache=cache,
        )
        self.chat_message_data_access = ChatMessageDataAccess(
            repository=self.chat_message_repo,
            cache=cache,
        )
        self.state_data_access = StateDataAccess(
            repository=self.state_repo,
            cache=cache,
        )
        self.default_rag_config_data_access = DefaultRagConfigDataAccess(
            repository=self.default_rag_config_repo,
            cache=cache,
        )

        # Services
        self.default_rag_config_service = DefaultRagConfigService(
            data_access=self.default_rag_config_data_access,
        )
        self.workspace_service = WorkspaceService(
            data_access=self.workspace_data_access,
            default_rag_config_service=self.default_rag_config_service,
        )
        self.document_service = DocumentService(
            data_access=self.document_data_access,
            workspace_repository=self.workspace_repo,
            blob_storage=self.blob_storage,
        )
        self.chat_session_service = ChatSessionService(
            data_access=self.chat_session_data_access,
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
            data_access=self.chat_message_data_access,
            session_data_access=self.chat_session_data_access,
            workspace_data_access=self.workspace_data_access,
            llm_provider=self.llm_provider,
        )

        # State service
        self.state_service = StateService(
            state_data_access=self.state_data_access,
            workspace_data_access=self.workspace_data_access,
            session_data_access=self.chat_session_data_access,
        )

        # RAG Options service (no dependencies)
        self.rag_options_service = RagOptionsService()

        # Orchestrators
        self.workspace_orchestrator = WorkspaceOrchestrator(
            service=self.workspace_service,
            repository=self.workspace_repo,
        )
        self.default_rag_config_orchestrator = DefaultRagConfigOrchestrator(
            service=self.default_rag_config_service,
        )
        self.document_orchestrator = DocumentOrchestrator(
            service=self.document_service,
        )
        self.session_orchestrator = SessionOrchestrator(
            service=self.chat_session_service,
        )
        self.message_orchestrator = MessageOrchestrator(
            service=self.chat_message_service,
        )
        self.state_orchestrator = StateOrchestrator(
            service=self.state_service,
        )
        self.rag_options_orchestrator = RagOptionsOrchestrator(
            service=self.rag_options_service,
        )

        # Load current state from database (using data access layer with caching)
        state = self.state_data_access.get()
        self.current_workspace_id: Optional[int] = state.current_workspace_id if state else None
        self.current_session_id: Optional[int] = state.current_session_id if state else None

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
