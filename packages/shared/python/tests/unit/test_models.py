"""
Unit tests for data models.

These tests verify the model classes (User, Document, Workspace, Chat)
correctly handle input data and produce expected output.
"""

from datetime import datetime


from shared.models.chat import ChatMessage, ChatSession
from shared.models.document import Document
from shared.models.user import User
from shared.models.workspace import RagConfig, Workspace


class TestUserModel:
    """Test User model input/output."""

    def test_user_creation_with_required_fields(self) -> None:
        """User can be created with required fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed"

    def test_user_default_values(self) -> None:
        """User has correct default values."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
        )

        assert user.id == 0
        assert user.full_name is None
        assert user.theme_preference == "dark"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_with_all_fields(self) -> None:
        """User can be created with all fields."""
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 2, 12, 0, 0)

        user = User(
            id=42,
            username="fulluser",
            email="full@example.com",
            password_hash="hash123",
            full_name="Full User Name",
            theme_preference="light",
            created_at=created,
            updated_at=updated,
        )

        assert user.id == 42
        assert user.username == "fulluser"
        assert user.email == "full@example.com"
        assert user.password_hash == "hash123"
        assert user.full_name == "Full User Name"
        assert user.theme_preference == "light"
        assert user.created_at == created
        assert user.updated_at == updated

    def test_user_repr(self) -> None:
        """User repr returns expected format."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
        )

        result = repr(user)

        assert result == "<User(id=1, username=testuser, email=test@example.com)>"

    def test_set_password_hashes_password(self) -> None:
        """set_password creates a bcrypt hash."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="",
        )

        user.set_password("mysecretpassword")

        # Hash should be set and different from plain password
        assert user.password_hash != ""
        assert user.password_hash != "mysecretpassword"
        # bcrypt hashes start with $2b$
        assert user.password_hash.startswith("$2b$")

    def test_check_password_returns_true_for_correct_password(self) -> None:
        """check_password returns True for correct password."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="",
        )
        user.set_password("correctpassword")

        result = user.check_password("correctpassword")

        assert result is True

    def test_check_password_returns_false_for_wrong_password(self) -> None:
        """check_password returns False for incorrect password."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="",
        )
        user.set_password("correctpassword")

        result = user.check_password("wrongpassword")

        assert result is False

    def test_hash_password_static_method(self) -> None:
        """hash_password static method returns bcrypt hash."""
        password = "testpassword"

        hashed = User.hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_hash_password_produces_unique_hashes(self) -> None:
        """hash_password produces different hashes for same password."""
        password = "samepassword"

        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)

        # bcrypt uses random salt, so hashes should differ
        assert hash1 != hash2

    def test_set_password_updates_hash(self) -> None:
        """set_password updates existing hash."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="oldhash",
        )

        user.set_password("newpassword")

        assert user.password_hash != "oldhash"
        assert user.check_password("newpassword") is True


class TestDocumentModel:
    """Test Document model input/output."""

    def test_document_creation_with_required_fields(self) -> None:
        """Document can be created with required fields."""
        doc = Document(
            id=1,
            user_id=10,
            filename="test.pdf",
            file_path="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="abc123",
        )

        assert doc.id == 1
        assert doc.user_id == 10
        assert doc.filename == "test.pdf"
        assert doc.file_path == "/storage/test.pdf"
        assert doc.file_size == 1024
        assert doc.mime_type == "application/pdf"
        assert doc.content_hash == "abc123"

    def test_document_default_values(self) -> None:
        """Document has correct default values."""
        doc = Document(
            id=1,
            user_id=10,
            filename="test.pdf",
            file_path="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="abc123",
        )

        assert doc.workspace_id is None
        assert doc.chunk_count is None
        assert doc.rag_collection is None
        assert doc.processing_status == "pending"
        assert doc.processing_error is None
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)

    def test_document_with_all_fields(self) -> None:
        """Document can be created with all fields."""
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 2, 12, 0, 0)

        doc = Document(
            id=1,
            user_id=10,
            filename="test.pdf",
            file_path="/storage/test.pdf",
            file_size=2048,
            mime_type="application/pdf",
            content_hash="hash123",
            workspace_id=5,
            chunk_count=100,
            rag_collection="collection_v1",
            processing_status="ready",
            processing_error=None,
            created_at=created,
            updated_at=updated,
        )

        assert doc.workspace_id == 5
        assert doc.chunk_count == 100
        assert doc.rag_collection == "collection_v1"
        assert doc.processing_status == "ready"
        assert doc.created_at == created
        assert doc.updated_at == updated

    def test_document_processing_status_values(self) -> None:
        """Document processing_status accepts valid values."""
        statuses = ["pending", "processing", "ready", "failed"]

        for status in statuses:
            doc = Document(
                id=1,
                user_id=1,
                filename="test.pdf",
                file_path="/path",
                file_size=100,
                mime_type="application/pdf",
                content_hash="hash",
                processing_status=status,
            )
            assert doc.processing_status == status

    def test_document_with_processing_error(self) -> None:
        """Document can store processing error message."""
        doc = Document(
            id=1,
            user_id=1,
            filename="test.pdf",
            file_path="/path",
            file_size=100,
            mime_type="application/pdf",
            content_hash="hash",
            processing_status="failed",
            processing_error="Failed to parse PDF: corrupted file",
        )

        assert doc.processing_status == "failed"
        assert doc.processing_error == "Failed to parse PDF: corrupted file"

    def test_document_repr(self) -> None:
        """Document repr returns expected format."""
        doc = Document(
            id=42,
            user_id=10,
            filename="report.pdf",
            file_path="/storage/report.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="abc",
        )

        result = repr(doc)

        assert result == "<Document(id=42, filename=report.pdf, user_id=10)>"


class TestWorkspaceModel:
    """Test Workspace model input/output."""

    def test_workspace_creation_with_required_fields(self) -> None:
        """Workspace can be created with required fields."""
        workspace = Workspace(
            user_id=1,
            name="My Workspace",
        )

        assert workspace.user_id == 1
        assert workspace.name == "My Workspace"

    def test_workspace_default_values(self) -> None:
        """Workspace has correct default values."""
        workspace = Workspace(
            user_id=1,
            name="My Workspace",
        )

        assert workspace.id == 0
        assert workspace.description is None
        assert workspace.is_active is True
        assert workspace.status == "provisioning"
        assert workspace.status_message is None
        assert isinstance(workspace.created_at, datetime)
        assert isinstance(workspace.updated_at, datetime)

    def test_workspace_with_all_fields(self) -> None:
        """Workspace can be created with all fields."""
        created = datetime(2024, 1, 1)
        updated = datetime(2024, 1, 2)

        workspace = Workspace(
            id=10,
            user_id=1,
            name="Full Workspace",
            description="A complete workspace",
            is_active=False,
            status="ready",
            status_message="Provisioning complete",
            created_at=created,
            updated_at=updated,
        )

        assert workspace.id == 10
        assert workspace.description == "A complete workspace"
        assert workspace.is_active is False
        assert workspace.status == "ready"
        assert workspace.status_message == "Provisioning complete"
        assert workspace.created_at == created
        assert workspace.updated_at == updated

    def test_workspace_status_values(self) -> None:
        """Workspace status accepts valid values."""
        statuses = ["provisioning", "ready", "error"]

        for status in statuses:
            workspace = Workspace(
                user_id=1,
                name="Test",
                status=status,
            )
            assert workspace.status == status

    def test_workspace_repr(self) -> None:
        """Workspace repr returns expected format."""
        workspace = Workspace(
            id=5,
            user_id=1,
            name="Test Workspace",
        )

        result = repr(workspace)

        assert result == "<Workspace(id=5, name=Test Workspace, user_id=1)>"


class TestRagConfigModel:
    """Test RagConfig model input/output."""

    def test_rag_config_creation_with_required_fields(self) -> None:
        """RagConfig can be created with required field."""
        config = RagConfig(workspace_id=1)

        assert config.workspace_id == 1

    def test_rag_config_default_values(self) -> None:
        """RagConfig has correct default values."""
        config = RagConfig(workspace_id=1)

        assert config.id == 0
        assert config.embedding_model == "nomic-embed-text"
        assert config.embedding_dim is None
        assert config.retriever_type == "vector"
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.top_k == 8
        assert config.rerank_enabled is False
        assert config.rerank_model is None
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)

    def test_rag_config_with_all_fields(self) -> None:
        """RagConfig can be created with all fields."""
        created = datetime(2024, 1, 1)
        updated = datetime(2024, 1, 2)

        config = RagConfig(
            id=10,
            workspace_id=5,
            embedding_model="text-embedding-3-small",
            embedding_dim=1536,
            retriever_type="hybrid",
            chunk_size=500,
            chunk_overlap=100,
            top_k=10,
            rerank_enabled=True,
            rerank_model="cohere-rerank-v3",
            created_at=created,
            updated_at=updated,
        )

        assert config.id == 10
        assert config.workspace_id == 5
        assert config.embedding_model == "text-embedding-3-small"
        assert config.embedding_dim == 1536
        assert config.retriever_type == "hybrid"
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.top_k == 10
        assert config.rerank_enabled is True
        assert config.rerank_model == "cohere-rerank-v3"

    def test_rag_config_retriever_types(self) -> None:
        """RagConfig retriever_type accepts valid values."""
        types = ["vector", "graph", "hybrid"]

        for retriever_type in types:
            config = RagConfig(
                workspace_id=1,
                retriever_type=retriever_type,
            )
            assert config.retriever_type == retriever_type

    def test_rag_config_repr(self) -> None:
        """RagConfig repr returns expected format."""
        config = RagConfig(
            id=3,
            workspace_id=1,
            retriever_type="graph",
        )

        result = repr(config)

        assert result == "<RagConfig(id=3, workspace_id=1, retriever_type=graph)>"


class TestChatSessionModel:
    """Test ChatSession model input/output."""

    def test_chat_session_creation_with_required_fields(self) -> None:
        """ChatSession can be created with required fields."""
        session = ChatSession(
            id=1,
            user_id=10,
        )

        assert session.id == 1
        assert session.user_id == 10

    def test_chat_session_default_values(self) -> None:
        """ChatSession has correct default values."""
        session = ChatSession(
            id=1,
            user_id=10,
        )

        assert session.workspace_id is None
        assert session.title is None
        assert session.rag_type == "vector"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)

    def test_chat_session_with_all_fields(self) -> None:
        """ChatSession can be created with all fields."""
        created = datetime(2024, 1, 1)
        updated = datetime(2024, 1, 2)

        session = ChatSession(
            id=5,
            user_id=10,
            workspace_id=3,
            title="Project Discussion",
            rag_type="graph",
            created_at=created,
            updated_at=updated,
        )

        assert session.id == 5
        assert session.user_id == 10
        assert session.workspace_id == 3
        assert session.title == "Project Discussion"
        assert session.rag_type == "graph"
        assert session.created_at == created
        assert session.updated_at == updated

    def test_chat_session_rag_types(self) -> None:
        """ChatSession rag_type accepts valid values."""
        types = ["vector", "graph"]

        for rag_type in types:
            session = ChatSession(
                id=1,
                user_id=1,
                rag_type=rag_type,
            )
            assert session.rag_type == rag_type

    def test_chat_session_repr(self) -> None:
        """ChatSession repr returns expected format."""
        session = ChatSession(
            id=42,
            user_id=10,
            title="Test Chat",
        )

        result = repr(session)

        assert result == "<ChatSession(id=42, user_id=10, title=Test Chat)>"

    def test_chat_session_repr_none_title(self) -> None:
        """ChatSession repr handles None title."""
        session = ChatSession(
            id=42,
            user_id=10,
        )

        result = repr(session)

        assert result == "<ChatSession(id=42, user_id=10, title=None)>"


class TestChatMessageModel:
    """Test ChatMessage model input/output."""

    def test_chat_message_creation_with_required_fields(self) -> None:
        """ChatMessage can be created with required fields."""
        message = ChatMessage(
            id=1,
            session_id=10,
            role="user",
            content="Hello, how can I help?",
        )

        assert message.id == 1
        assert message.session_id == 10
        assert message.role == "user"
        assert message.content == "Hello, how can I help?"

    def test_chat_message_default_values(self) -> None:
        """ChatMessage has correct default values."""
        message = ChatMessage(
            id=1,
            session_id=10,
            role="user",
            content="Test",
        )

        assert message.extra_metadata is None
        assert isinstance(message.created_at, datetime)
        assert isinstance(message.updated_at, datetime)

    def test_chat_message_with_all_fields(self) -> None:
        """ChatMessage can be created with all fields."""
        created = datetime(2024, 1, 1)
        updated = datetime(2024, 1, 2)

        message = ChatMessage(
            id=5,
            session_id=10,
            role="assistant",
            content="I can help you with that.",
            extra_metadata='{"sources": ["doc1.pdf", "doc2.pdf"]}',
            created_at=created,
            updated_at=updated,
        )

        assert message.id == 5
        assert message.session_id == 10
        assert message.role == "assistant"
        assert message.content == "I can help you with that."
        assert message.extra_metadata == '{"sources": ["doc1.pdf", "doc2.pdf"]}'
        assert message.created_at == created
        assert message.updated_at == updated

    def test_chat_message_roles(self) -> None:
        """ChatMessage role accepts valid values."""
        roles = ["user", "assistant", "system"]

        for role in roles:
            message = ChatMessage(
                id=1,
                session_id=1,
                role=role,
                content="Test",
            )
            assert message.role == role

    def test_chat_message_repr_short_content(self) -> None:
        """ChatMessage repr shows full short content."""
        message = ChatMessage(
            id=1,
            session_id=10,
            role="user",
            content="Short message",
        )

        result = repr(message)

        assert result == "<ChatMessage(id=1, session_id=10, role=user, content='Short message')>"

    def test_chat_message_repr_long_content(self) -> None:
        """ChatMessage repr truncates long content."""
        long_content = "A" * 100

        message = ChatMessage(
            id=1,
            session_id=10,
            role="assistant",
            content=long_content,
        )

        result = repr(message)

        # Content should be truncated to 50 chars + "..."
        assert "content='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...'" in result

    def test_chat_message_repr_exactly_50_chars(self) -> None:
        """ChatMessage repr handles exactly 50 char content."""
        content_50 = "A" * 50

        message = ChatMessage(
            id=1,
            session_id=10,
            role="user",
            content=content_50,
        )

        result = repr(message)

        assert f"content='{content_50}'" in result
        assert "..." not in result
