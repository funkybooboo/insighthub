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

        from src.domains.workspaces.chat.messages.service import ChatMessageService
        from src.domains.workspaces.chat.sessions.service import ChatSessionService

        self.chat_session_service = ChatSessionService(repository=session_repo)
        self.chat_message_service = ChatMessageService(repository=message_repo)

        # Initialize workspace service (required)
        workspace_repo = create_workspace_repository()
        self.workspace_service = WorkspaceService(repository=workspace_repo)

        # Initialize document service (required)
        document_repo = create_document_repository()
        self.document_service = DocumentService(
            repository=document_repo, blob_storage=self.blob_storage
        )

        # Initialize document processor for background processing
        # Note: socketio will be set later when the socket handler is initialized
        from src.infrastructure.rag.workflows.factory import (
            WorkflowFactory,
            create_default_vector_rag_config,
        )
        from src.workers.document_processing_worker import initialize_document_processor

        # Create workflow using factory with default config
        # TODO: Get RAG config from workspace settings instead of default
        rag_config = create_default_vector_rag_config()
        consume_workflow = WorkflowFactory.create_consume_workflow(rag_config)

        self.document_processor = initialize_document_processor(
            repository=document_repo,
            blob_storage=self.blob_storage,
            socketio=None,  # Will be updated when socketio becomes available
            consume_workflow=consume_workflow,
        )

        # Initialize default RAG config service (required)
        default_rag_config_repo = create_default_rag_config_repository()
        self.default_rag_config_service = DefaultRagConfigService(
            repository=default_rag_config_repo
        )

        # Initialize infrastructure components
        self.cache = create_cache()
        self.llm_provider = create_llm_provider(
            provider_type="ollama", base_url="http://localhost:11434", model_name="llama3.2"
        )
        self.blob_storage = create_blob_storage(storage_type="filesystem")
