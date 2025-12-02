"""Application context containing all services and repositories."""

from src.config import config
from src.domains.default_rag_configs.service import DefaultRagConfigService
from src.domains.workspaces.chats.messages.service import ChatMessageService
from src.domains.workspaces.chats.sessions.service import ChatSessionService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.sql_database import get_sql_database
from src.infrastructure.llm.factory import create_llm_provider
from src.infrastructure.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DefaultRagConfigRepository,
    DocumentRepository,
    WorkspaceRepository,
)
from src.infrastructure.storage.factory import create_blob_storage


class AppContext:
    """Application context containing all services and repositories."""

    def __init__(self):
        """Initialize context with all services."""
        # Database
        db = get_sql_database()

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

        # Services
        self.workspace_service = WorkspaceService(repository=self.workspace_repo)
        self.document_service = DocumentService(
            repository=self.document_repo, blob_storage=self.blob_storage
        )
        self.default_rag_config_service = DefaultRagConfigService(
            repository=self.default_rag_config_repo
        )
        self.chat_session_service = ChatSessionService(repository=self.chat_session_repo)
        self.chat_message_service = ChatMessageService(repository=self.chat_message_repo)

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

        # Global state for selected workspace and session
        self.current_workspace_id: int | None = None
        self.current_session_id: int | None = None
