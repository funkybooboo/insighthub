"""Application context for dependency injection and service management."""

from src.domains.auth.service import UserService
from src.domains.default_rag_configs.service import DefaultRagConfigService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.service import WorkspaceService
from src.infrastructure import config
from src.infrastructure.cache.factory import create_cache
from src.infrastructure.llm.factory import create_llm_provider
from src.infrastructure.repositories.chat_messages.factory import create_chat_message_repository
from src.infrastructure.repositories.chat_sessions.factory import create_chat_session_repository
from src.infrastructure.repositories.default_rag_configs.factory import (
    create_default_rag_config_repository,
)
from src.infrastructure.repositories.documents.factory import create_document_repository
from src.infrastructure.repositories.users.factory import create_user_repository
from src.infrastructure.repositories.workspaces.factory import create_workspace_repository
from src.infrastructure.storage.factory import create_blob_storage


class AppContext:
    """Application context containing all services and dependencies."""

    def __init__(self, db=None):
        """Initialize the application context with all services."""
        # Validate required configuration
        required_configs = ["DATABASE_URL"]
        for config_key in required_configs:
            if not hasattr(config, config_key) or not getattr(config, config_key):
                raise ValueError(f"Required configuration '{config_key}' is missing")

        # Initialize users service (required)
        db_url = getattr(config, "DATABASE_URL", "sqlite:///insighthub.db")
        user_repo = create_user_repository(db_type="sqlite", db_url=db_url)
        self.user_service = UserService(repository=user_repo)

        # Initialize chat services (required)
        session_repo = create_chat_session_repository()
        message_repo = create_chat_message_repository()

        from src.domains.workspaces.chats.messages.service import ChatMessageService
        from src.domains.workspaces.chats.sessions.service import ChatSessionService

        self.chat_session_service = ChatSessionService(repository=session_repo)
        self.chat_message_service = ChatMessageService(repository=message_repo)

        # Initialize infrastructure components first
        self.cache = create_cache()
        self.llm_provider = create_llm_provider(
            provider_type="ollama", base_url="http://localhost:11434", model_name="llama3.2"
        )
        self.blob_storage = create_blob_storage(storage_type="filesystem")

        # Initialize workspace service (required)
        workspace_repo = create_workspace_repository()
        self.workspace_service = WorkspaceService(repository=workspace_repo)

        # Initialize document service (required)
        document_repo = create_document_repository()
        self.document_service = DocumentService(
            repository=document_repo, blob_storage=self.blob_storage
        )

        # Store repositories for worker initialization
        self.document_repo = document_repo
        self.workspace_repo = workspace_repo
        self.session_repo = session_repo
        self.message_repo = message_repo

        # Initialize default RAG config service (required)
        default_rag_config_repo = create_default_rag_config_repository()
        self.default_rag_config_service = DefaultRagConfigService(
            repository=default_rag_config_repo
        )

    def initialize_workers(self, socketio) -> None:
        """
        Initialize all background workers with SocketIO instance.

        This should be called after SocketIO is created in the Flask app.

        Args:
            socketio: Flask-SocketIO instance for real-time updates
        """
        from src.workers import (
            initialize_add_document_worker,
            initialize_chat_query_worker,
            initialize_remove_document_worker,
            initialize_remove_workspace_worker,
            initialize_create_workspace_worker,
        )

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

        initialize_create_workspace_worker(
            repository=self.workspace_repo,
            socketio=socketio,
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
