"""Application context for dependency injection and service management."""

import threading

from src import config
from src.domains.auth.service import UserService
from src.domains.default_rag_configs.service import DefaultRagConfigService
from src.domains.health.service import HealthService
from src.domains.workspaces.chats.messages.service import ChatMessageService
from src.domains.workspaces.chats.service import ChatService
from src.domains.workspaces.chats.sessions.service import ChatSessionService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.cache.factory import create_cache
from src.infrastructure.llm.factory import create_llm_provider
from src.infrastructure.logger import create_logger
from src.infrastructure.repositories.chat_messages.factory import create_chat_message_repository
from src.infrastructure.repositories.chat_sessions.factory import create_chat_session_repository
from src.infrastructure.repositories.default_rag_configs.factory import (
    create_default_rag_config_repository,
)
from src.infrastructure.repositories.documents.factory import create_document_repository
from src.infrastructure.repositories.users.factory import create_user_repository
from src.infrastructure.repositories.workspaces.factory import create_workspace_repository
from src.infrastructure.storage.factory import create_blob_storage
from src.workers import (
    initialize_add_document_worker,
    initialize_chat_query_worker,
    initialize_create_workspace_worker,
    initialize_fetch_wikipedia_worker,
    initialize_remove_document_worker,
    initialize_remove_workspace_worker,
)

logger = create_logger(__name__)


class AppContext:
    """Application context containing all services and dependencies."""

    def __init__(self, db, socketio):
        """Initialize the application context with all services."""
        # Initialize users service (required)
        user_repo_type = getattr(config, "user_repository_type", "in_memory")
        user_repo = create_user_repository(repo_type=user_repo_type, db=db)
        self.user_service = UserService(repository=user_repo)

        # Initialize chat services (required)
        chat_session_repo_type = getattr(config, "chat_session_repository_type", "in_memory")
        chat_message_repo_type = getattr(config, "chat_message_repository_type", "in_memory")
        session_repo = create_chat_session_repository(repo_type=chat_session_repo_type, db=db)
        message_repo = create_chat_message_repository(repo_type=chat_message_repo_type, db=db)

        self.chat_session_service = ChatSessionService(repository=session_repo)
        self.chat_message_service = ChatMessageService(repository=message_repo)
        self.chat_service = ChatService(
            message_service=self.chat_message_service, session_service=self.chat_session_service
        )

        # Initialize infrastructure components first
        cache_type = getattr(config, "cache_type", "in_memory")
        redis_url = getattr(config, "redis_url", None)
        self.cache = create_cache(cache_type=cache_type, redis_url=redis_url)

        llm_provider_type = getattr(config, "llm_provider", "ollama")
        ollama_base_url = getattr(config, "ollama_base_url", "http://localhost:11434")
        ollama_llm_model = getattr(config, "ollama_llm_model", "llama3.2")

        # Get API key based on provider
        api_key = None
        if llm_provider_type == "openai":
            api_key = getattr(config, "openai_api_key", None)
        elif llm_provider_type == "claude":
            api_key = getattr(config, "anthropic_api_key", None)
        elif llm_provider_type == "huggingface":
            api_key = getattr(config, "huggingface_api_key", None)

        self.llm_provider = create_llm_provider(
            provider_type=llm_provider_type,
            base_url=ollama_base_url,
            model_name=ollama_llm_model,
            api_key=api_key,
        )

        blob_storage_type = getattr(config, "blob_storage_type", "filesystem")
        self.blob_storage = create_blob_storage(
            storage_type=blob_storage_type,
            file_system_path=getattr(config, "file_system_storage_path", "uploads"),
            s3_endpoint_url=getattr(config, "s3_endpoint_url", None),
            s3_access_key=getattr(config, "s3_access_key", None),
            s3_secret_key=getattr(config, "s3_secret_key", None),
            s3_bucket_name=getattr(config, "s3_bucket_name", "documents"),
        )

        # Initialize workspace service (required)
        workspace_repo_type = getattr(config, "workspace_repository_type", "in_memory")
        workspace_repo = create_workspace_repository(repo_type=workspace_repo_type, db=db)
        self.workspace_service = WorkspaceService(repository=workspace_repo)

        # Initialize document service (required)
        document_repo_type = getattr(config, "document_repository_type", "in_memory")
        document_repo = create_document_repository(repo_type=document_repo_type, db=db)
        self.document_service = DocumentService(
            repository=document_repo, blob_storage=self.blob_storage
        )

        # Store repositories for worker initialization
        self.document_repo = document_repo
        self.workspace_repo = workspace_repo
        self.session_repo = session_repo
        self.message_repo = message_repo

        # Initialize default RAG config service (required)
        default_rag_config_repo_type = getattr(
            config, "default_rag_config_repository_type", "in_memory"
        )
        default_rag_config_repo = create_default_rag_config_repository(
            repo_type=default_rag_config_repo_type, db=db
        )
        self.default_rag_config_service = DefaultRagConfigService(
            repository=default_rag_config_repo
        )

        # Initialize health service (required)
        self.health_service = HealthService()

        # Initialize all workers
        initialize_add_document_worker(
            document_repository=self.document_repo,
            workspace_repository=self.workspace_repo,
            blob_storage=self.blob_storage,
            socketio=socketio,
        )

        initialize_remove_document_worker(
            document_repository=self.document_repo,
            workspace_repository=self.workspace_repo,
            blob_storage=self.blob_storage,
            socketio=socketio,
        )

        initialize_fetch_wikipedia_worker(
            document_repository=self.document_repo,
            workspace_repository=self.workspace_repo,
            blob_storage=self.blob_storage,
            socketio=socketio,
        )

        initialize_create_workspace_worker(
            repository=self.workspace_repo,
            socketio=socketio,
            config=config,
        )

        initialize_remove_workspace_worker(
            workspace_repository=self.workspace_repo,
            document_repository=self.document_repo,
            blob_storage=self.blob_storage,
            socketio=socketio,
        )

        initialize_chat_query_worker(
            message_repository=self.message_repo,
            session_repository=self.session_repo,
            workspace_repository=self.workspace_repo,
            socketio=socketio,
            llm_provider=self.llm_provider,
        )

        logger.info("Background workers initialized successfully")


# Singleton instance and lock for thread safety
_app_context_instance: AppContext | None = None
_app_context_lock = threading.Lock()


def create_app_context(db, socketio) -> AppContext:
    """Create or return the singleton application context instance.

    Args:
        socketio:
        db:

    Returns:
        Singleton AppContext instance
    """
    global _app_context_instance

    if _app_context_instance is None:
        with _app_context_lock:
            # Double-check pattern for thread safety
            if _app_context_instance is None:
                _app_context_instance = AppContext(db, socketio)

    return _app_context_instance


def get_app_context() -> AppContext:
    if not _app_context_instance:
        raise Exception("call create_app_context first")
    return _app_context_instance


def reset_app_context() -> None:
    """Reset the singleton application context instance.

    This is primarily for testing purposes.
    """
    global _app_context_instance

    with _app_context_lock:
        _app_context_instance = None
