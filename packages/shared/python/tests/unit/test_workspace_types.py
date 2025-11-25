"""Unit tests for workspace types."""

import pytest
from datetime import datetime, UTC
from shared.types.workspace import (
    Workspace,
    RagConfig,
    WorkspaceDocument,
    ChatSession,
    ChatMessage,
    WorkspaceStats,
)
from shared.types.common import DocumentStatus


class TestWorkspace:
    """Test Workspace dataclass."""

    def test_workspace_creation_with_required_fields(self) -> None:
        """Test creating a workspace with all required fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        workspace = Workspace(
            id="ws-123",
            name="Test Workspace",
            created_at=created_at,
            updated_at=updated_at,
            user_id="user-456",
        )

        assert workspace.id == "ws-123"
        assert workspace.name == "Test Workspace"
        assert workspace.created_at == created_at
        assert workspace.updated_at == updated_at
        assert workspace.user_id == "user-456"
        assert workspace.description is None
        assert workspace.is_active is True

    def test_workspace_creation_with_optional_fields(self) -> None:
        """Test creating a workspace with optional fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        workspace = Workspace(
            id="ws-123",
            name="Test Workspace",
            created_at=created_at,
            updated_at=updated_at,
            user_id="user-456",
            description="A test workspace",
            is_active=False,
        )

        assert workspace.description == "A test workspace"
        assert workspace.is_active is False

    def test_workspace_immutable_fields(self) -> None:
        """Test that workspace fields can be modified (dataclass is mutable)."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        workspace = Workspace(
            id="ws-123",
            name="Test Workspace",
            created_at=created_at,
            updated_at=updated_at,
            user_id="user-456",
        )

        # Test field modification
        workspace.name = "Updated Name"
        workspace.description = "New description"
        workspace.is_active = False

        assert workspace.name == "Updated Name"
        assert workspace.description == "New description"
        assert workspace.is_active is False


class TestRagConfig:
    """Test RagConfig dataclass."""

    def test_rag_config_creation_with_required_fields(self) -> None:
        """Test creating a RAG config with required fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        config = RagConfig(
            id="config-123",
            workspace_id="ws-456",
            embedding_model="nomic-embed-text",
            retriever_type="vector",
            chunk_size=1000,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert config.id == "config-123"
        assert config.workspace_id == "ws-456"
        assert config.embedding_model == "nomic-embed-text"
        assert config.retriever_type == "vector"
        assert config.chunk_size == 1000
        assert config.created_at == created_at
        assert config.updated_at == updated_at
        assert config.chunk_overlap == 0
        assert config.top_k == 8
        assert config.embedding_dim is None
        assert config.rerank_enabled is False
        assert config.rerank_model is None

    def test_rag_config_creation_with_optional_fields(self) -> None:
        """Test creating a RAG config with optional fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        config = RagConfig(
            id="config-123",
            workspace_id="ws-456",
            embedding_model="nomic-embed-text",
            retriever_type="vector",
            chunk_size=1000,
            created_at=created_at,
            updated_at=updated_at,
            chunk_overlap=200,
            top_k=5,
            embedding_dim=768,
            rerank_enabled=True,
            rerank_model="rerank-model",
        )

        assert config.chunk_overlap == 200
        assert config.top_k == 5
        assert config.embedding_dim == 768
        assert config.rerank_enabled is True
        assert config.rerank_model == "rerank-model"


class TestWorkspaceDocument:
    """Test WorkspaceDocument dataclass."""

    def test_workspace_document_creation_with_required_fields(self) -> None:
        """Test creating a workspace document with required fields."""
        uploaded_at = datetime.now(UTC)

        doc = WorkspaceDocument(
            id="doc-123",
            workspace_id="ws-456",
            filename="test.pdf",
            storage_path="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            uploaded_at=uploaded_at,
            user_id="user-789",
        )

        assert doc.id == "doc-123"
        assert doc.workspace_id == "ws-456"
        assert doc.filename == "test.pdf"
        assert doc.storage_path == "/storage/test.pdf"
        assert doc.file_size == 1024
        assert doc.mime_type == "application/pdf"
        assert doc.uploaded_at == uploaded_at
        assert doc.user_id == "user-789"
        assert doc.status == DocumentStatus.PENDING
        assert doc.processing_error is None
        assert doc.chunk_count is None
        assert doc.embedding_status is None
        assert doc.title is None
        assert doc.author is None
        assert doc.created_date is None

    def test_workspace_document_creation_with_optional_fields(self) -> None:
        """Test creating a workspace document with optional fields."""
        uploaded_at = datetime.now(UTC)
        created_date = datetime.now(UTC)

        doc = WorkspaceDocument(
            id="doc-123",
            workspace_id="ws-456",
            filename="test.pdf",
            storage_path="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            uploaded_at=uploaded_at,
            user_id="user-789",
            status=DocumentStatus.COMPLETED,
            processing_error="Some error",
            chunk_count=10,
            embedding_status="completed",
            title="Test Document",
            author="Test Author",
            created_date=created_date,
        )

        assert doc.status == DocumentStatus.COMPLETED
        assert doc.processing_error == "Some error"
        assert doc.chunk_count == 10
        assert doc.embedding_status == "completed"
        assert doc.title == "Test Document"
        assert doc.author == "Test Author"
        assert doc.created_date == created_date


class TestChatSession:
    """Test ChatSession dataclass."""

    def test_chat_session_creation_with_required_fields(self) -> None:
        """Test creating a chat session with required fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        session = ChatSession(
            id="session-123",
            workspace_id="ws-456",
            title="Test Chat",
            created_at=created_at,
            updated_at=updated_at,
            user_id="user-789",
        )

        assert session.id == "session-123"
        assert session.workspace_id == "ws-456"
        assert session.title == "Test Chat"
        assert session.created_at == created_at
        assert session.updated_at == updated_at
        assert session.user_id == "user-789"
        assert session.is_active is True
        assert session.system_prompt is None
        assert session.temperature == 0.7
        assert session.max_tokens is None

    def test_chat_session_creation_with_optional_fields(self) -> None:
        """Test creating a chat session with optional fields."""
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        session = ChatSession(
            id="session-123",
            workspace_id="ws-456",
            title="Test Chat",
            created_at=created_at,
            updated_at=updated_at,
            user_id="user-789",
            is_active=False,
            system_prompt="You are a helpful assistant",
            temperature=0.5,
            max_tokens=1000,
        )

        assert session.is_active is False
        assert session.system_prompt == "You are a helpful assistant"
        assert session.temperature == 0.5
        assert session.max_tokens == 1000


class TestChatMessage:
    """Test ChatMessage dataclass."""

    def test_chat_message_creation_with_required_fields(self) -> None:
        """Test creating a chat message with required fields."""
        created_at = datetime.now(UTC)

        message = ChatMessage(
            id="msg-123",
            session_id="session-456",
            role="user",
            content="Hello, world!",
            created_at=created_at,
        )

        assert message.id == "msg-123"
        assert message.session_id == "session-456"
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.created_at == created_at
        assert message.token_count is None
        assert message.model_used is None
        assert message.retrieval_results is None

    def test_chat_message_creation_with_optional_fields(self) -> None:
        """Test creating a chat message with optional fields."""
        created_at = datetime.now(UTC)
        retrieval_results = [{"score": 0.9, "content": "test"}]

        message = ChatMessage(
            id="msg-123",
            session_id="session-456",
            role="assistant",
            content="Hello back!",
            created_at=created_at,
            token_count=50,
            model_used="llama3.2",
            retrieval_results=retrieval_results,
        )

        assert message.role == "assistant"
        assert message.content == "Hello back!"
        assert message.token_count == 50
        assert message.model_used == "llama3.2"
        assert message.retrieval_results == retrieval_results

    def test_chat_message_roles(self) -> None:
        """Test different message roles."""
        created_at = datetime.now(UTC)

        # User message
        user_msg = ChatMessage(
            id="msg-1",
            session_id="session-456",
            role="user",
            content="User question",
            created_at=created_at,
        )
        assert user_msg.role == "user"

        # Assistant message
        assistant_msg = ChatMessage(
            id="msg-2",
            session_id="session-456",
            role="assistant",
            content="Assistant response",
            created_at=created_at,
        )
        assert assistant_msg.role == "assistant"

        # System message
        system_msg = ChatMessage(
            id="msg-3",
            session_id="session-456",
            role="system",
            content="System prompt",
            created_at=created_at,
        )
        assert system_msg.role == "system"


class TestWorkspaceStats:
    """Test WorkspaceStats dataclass."""

    def test_workspace_stats_creation_with_required_fields(self) -> None:
        """Test creating workspace stats with required fields."""
        last_activity = datetime.now(UTC)

        stats = WorkspaceStats(
            workspace_id="ws-123",
            document_count=5,
            total_document_size=1024000,
            chunk_count=500,
            chat_session_count=3,
            total_message_count=150,
            last_activity=last_activity,
        )

        assert stats.workspace_id == "ws-123"
        assert stats.document_count == 5
        assert stats.total_document_size == 1024000
        assert stats.chunk_count == 500
        assert stats.chat_session_count == 3
        assert stats.total_message_count == 150
        assert stats.last_activity == last_activity

    def test_workspace_stats_creation_without_last_activity(self) -> None:
        """Test creating workspace stats without last activity."""
        stats = WorkspaceStats(
            workspace_id="ws-123",
            document_count=0,
            total_document_size=0,
            chunk_count=0,
            chat_session_count=0,
            total_message_count=0,
        )

        assert stats.workspace_id == "ws-123"
        assert stats.document_count == 0
        assert stats.total_document_size == 0
        assert stats.chunk_count == 0
        assert stats.chat_session_count == 0
        assert stats.total_message_count == 0
        assert stats.last_activity is None

    def test_workspace_stats_zero_values(self) -> None:
        """Test workspace stats with zero values."""
        stats = WorkspaceStats(
            workspace_id="ws-empty",
            document_count=0,
            total_document_size=0,
            chunk_count=0,
            chat_session_count=0,
            total_message_count=0,
        )

        assert stats.document_count == 0
        assert stats.total_document_size == 0
        assert stats.chunk_count == 0
        assert stats.chat_session_count == 0
        assert stats.total_message_count == 0