"""Application context containing all services and repositories."""

from src.config import config
from src.domains.default_rag_configs.service import DefaultRagConfigService
from src.domains.workspaces.chats.messages.service import ChatMessageService
from src.domains.workspaces.chats.sessions.service import ChatSessionService
from src.domains.workspaces.documents.service import DocumentService
from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.llm.factory import create_llm_provider
from src.infrastructure.repositories.chat_messages.factory import (
    create_chat_message_repository,
)
from src.infrastructure.repositories.chat_sessions.factory import (
    create_chat_session_repository,
)
from src.infrastructure.repositories.default_rag_configs.factory import (
    create_default_rag_config_repository,
)
from src.infrastructure.repositories.documents.factory import create_document_repository
from src.infrastructure.repositories.workspaces.factory import create_workspace_repository
from src.infrastructure.storage.factory import create_blob_storage


class AppContext:
    """Application context containing all services and repositories."""

    def __init__(self):
        """Initialize context with all services."""
        # Storage
        blob_storage_type = getattr(config, "blob_storage_type", "filesystem")
        self.blob_storage = create_blob_storage(
            storage_type=blob_storage_type,
            file_system_path=getattr(config, "file_system_storage_path", "uploads"),
            s3_endpoint_url=getattr(config, "s3_endpoint_url", None),
            s3_access_key=getattr(config, "s3_access_key", None),
            s3_secret_key=getattr(config, "s3_secret_key", None),
            s3_bucket_name=getattr(config, "s3_bucket_name", "documents"),
        )

        # Repositories
        workspace_repo_type = getattr(config, "workspace_repository_type", "sql")
        self.workspace_repo = create_workspace_repository(
            repo_type=workspace_repo_type, db=None
        )

        document_repo_type = getattr(config, "document_repository_type", "sql")
        self.document_repo = create_document_repository(repo_type=document_repo_type, db=None)

        default_rag_config_repo_type = getattr(
            config, "default_rag_config_repository_type", "sql"
        )
        self.default_rag_config_repo = create_default_rag_config_repository(
            repo_type=default_rag_config_repo_type, db=None
        )

        chat_session_repo_type = getattr(config, "chat_session_repository_type", "sql")
        self.chat_session_repo = create_chat_session_repository(
            repo_type=chat_session_repo_type, db=None
        )

        chat_message_repo_type = getattr(config, "chat_message_repository_type", "sql")
        self.chat_message_repo = create_chat_message_repository(
            repo_type=chat_message_repo_type, db=None
        )

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
        llm_provider_type = getattr(config, "llm_provider", "ollama")
        ollama_base_url = getattr(config, "ollama_base_url", "http://localhost:11434")
        ollama_llm_model = getattr(config, "ollama_llm_model", "llama3.2")

        api_key = None
        if llm_provider_type == "openai":
            api_key = getattr(config, "openai_api_key", None)
        elif llm_provider_type == "claude":
            api_key = getattr(config, "anthropic_api_key", None)

        self.llm_provider = create_llm_provider(
            provider_type=llm_provider_type,
            base_url=ollama_base_url,
            model_name=ollama_llm_model,
            api_key=api_key,
        )

        # Global state for selected workspace and session
        self.current_workspace_id: int | None = None
        self.current_session_id: int | None = None
