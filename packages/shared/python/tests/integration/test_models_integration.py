"""
Integration tests for model classes.

These tests verify that models work correctly together
and integrate with other components.
"""

from datetime import datetime

from shared.models.chat import ChatMessage, ChatSession
from shared.models.document import Document
from shared.models.user import User
from shared.models.workspace import RagConfig, Workspace


class TestUserPasswordIntegration:
    """Integration tests for User password functionality."""

    def test_password_set_and_verify_workflow(self) -> None:
        """Complete password set and verify workflow."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="",
        )

        # Set password
        user.set_password("MySecurePassword123!")

        # Verify correct password works
        assert user.check_password("MySecurePassword123!") is True

        # Verify wrong passwords fail
        assert user.check_password("WrongPassword") is False
        assert user.check_password("mysecurepassword123!") is False  # case sensitive
        assert user.check_password("") is False

    def test_password_change_workflow(self) -> None:
        """User can change password and old password no longer works."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="",
        )

        # Set initial password
        user.set_password("InitialPassword")
        assert user.check_password("InitialPassword") is True

        # Change password
        user.set_password("NewPassword")

        # New password works, old doesn't
        assert user.check_password("NewPassword") is True
        assert user.check_password("InitialPassword") is False

    def test_static_hash_used_in_user(self) -> None:
        """Static hash_password can be used to create user with hashed password."""
        password = "UserPassword123"
        hashed = User.hash_password(password)

        user = User(
            username="newuser",
            email="new@example.com",
            password_hash=hashed,
        )

        # User should be able to verify with original password
        assert user.check_password(password) is True


class TestWorkspaceAndRagConfigIntegration:
    """Integration tests for Workspace and RagConfig relationship."""

    def test_workspace_with_rag_config(self) -> None:
        """Workspace and RagConfig can be associated."""
        workspace = Workspace(
            id=1,
            user_id=10,
            name="ML Research",
            description="Machine learning research workspace",
            status="ready",
        )

        rag_config = RagConfig(
            id=1,
            workspace_id=workspace.id,
            embedding_model="text-embedding-3-small",
            retriever_type="hybrid",
            chunk_size=500,
            top_k=10,
        )

        # Verify association
        assert rag_config.workspace_id == workspace.id
        assert workspace.id == 1
        assert rag_config.retriever_type == "hybrid"

    def test_multiple_rag_configs_different_workspaces(self) -> None:
        """Different workspaces can have different RAG configs."""
        ws1 = Workspace(id=1, user_id=1, name="Workspace 1")
        ws2 = Workspace(id=2, user_id=1, name="Workspace 2")

        config1 = RagConfig(
            workspace_id=ws1.id,
            retriever_type="vector",
            chunk_size=500,
        )

        config2 = RagConfig(
            workspace_id=ws2.id,
            retriever_type="graph",
            chunk_size=1000,
        )

        assert config1.workspace_id != config2.workspace_id
        assert config1.retriever_type == "vector"
        assert config2.retriever_type == "graph"


class TestChatSessionAndMessageIntegration:
    """Integration tests for ChatSession and ChatMessage relationship."""

    def test_chat_session_with_messages(self) -> None:
        """Chat session can have multiple messages."""
        session = ChatSession(
            id=1,
            user_id=10,
            workspace_id=5,
            title="Project Discussion",
        )

        messages = [
            ChatMessage(
                id=1,
                session_id=session.id,
                role="user",
                content="What is machine learning?",
            ),
            ChatMessage(
                id=2,
                session_id=session.id,
                role="assistant",
                content="Machine learning is a subset of AI...",
            ),
            ChatMessage(
                id=3,
                session_id=session.id,
                role="user",
                content="Can you give an example?",
            ),
        ]

        # All messages should reference the session
        for msg in messages:
            assert msg.session_id == session.id

        # Verify message order by id
        assert messages[0].id < messages[1].id < messages[2].id

    def test_multiple_sessions_isolated(self) -> None:
        """Messages from different sessions are isolated."""
        session1 = ChatSession(id=1, user_id=1)
        session2 = ChatSession(id=2, user_id=1)

        msg1 = ChatMessage(
            id=1, session_id=session1.id, role="user", content="Message in session 1"
        )
        msg2 = ChatMessage(
            id=2, session_id=session2.id, role="user", content="Message in session 2"
        )

        assert msg1.session_id != msg2.session_id


class TestDocumentWorkspaceIntegration:
    """Integration tests for Document and Workspace relationship."""

    def test_document_in_workspace(self) -> None:
        """Document can be associated with a workspace."""
        workspace = Workspace(
            id=5,
            user_id=1,
            name="Research Papers",
        )

        doc = Document(
            id=100,
            user_id=1,
            filename="paper.pdf",
            file_path="/storage/paper.pdf",
            file_size=2048,
            mime_type="application/pdf",
            content_hash="abc123",
            workspace_id=workspace.id,
        )

        assert doc.workspace_id == workspace.id
        assert doc.workspace_id == 5

    def test_document_without_workspace(self) -> None:
        """Document can exist without workspace."""
        doc = Document(
            id=100,
            user_id=1,
            filename="standalone.pdf",
            file_path="/storage/standalone.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="def456",
        )

        assert doc.workspace_id is None


class TestModelTimestamps:
    """Integration tests for model timestamp handling."""

    def test_all_models_have_timestamps(self) -> None:
        """All models have created_at and updated_at timestamps."""
        user = User(username="test", email="test@test.com", password_hash="hash")
        doc = Document(
            id=1,
            user_id=1,
            filename="f",
            file_path="p",
            file_size=1,
            mime_type="t",
            content_hash="h",
        )
        workspace = Workspace(user_id=1, name="ws")
        config = RagConfig(workspace_id=1)
        session = ChatSession(id=1, user_id=1)
        message = ChatMessage(id=1, session_id=1, role="user", content="c")

        models = [user, doc, workspace, config, session, message]

        for model in models:
            assert hasattr(model, "created_at")
            assert hasattr(model, "updated_at")
            assert isinstance(model.created_at, datetime)
            assert isinstance(model.updated_at, datetime)

    def test_custom_timestamps_preserved(self) -> None:
        """Custom timestamps are preserved when provided."""
        created = datetime(2023, 1, 1, 10, 0, 0)
        updated = datetime(2024, 6, 15, 15, 30, 0)

        user = User(
            username="test",
            email="test@test.com",
            password_hash="hash",
            created_at=created,
            updated_at=updated,
        )

        assert user.created_at == created
        assert user.updated_at == updated


class TestModelDataIntegrity:
    """Integration tests for model data integrity."""

    def test_user_email_format(self) -> None:
        """User stores email as provided."""
        emails = [
            "simple@example.com",
            "user.name+tag@example.co.uk",
            "test123@subdomain.example.org",
        ]

        for email in emails:
            user = User(username="test", email=email, password_hash="hash")
            assert user.email == email

    def test_document_mime_types(self) -> None:
        """Document stores various mime types correctly."""
        mime_types = [
            "application/pdf",
            "text/plain",
            "text/html",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/png",
        ]

        for mime_type in mime_types:
            doc = Document(
                id=1,
                user_id=1,
                filename="test",
                file_path="/path",
                file_size=100,
                mime_type=mime_type,
                content_hash="hash",
            )
            assert doc.mime_type == mime_type

    def test_workspace_status_transitions(self) -> None:
        """Workspace status can represent different states."""
        ws = Workspace(user_id=1, name="Test", status="provisioning")
        assert ws.status == "provisioning"

        # Simulate status transition
        ws.status = "ready"
        assert ws.status == "ready"

        ws.status = "error"
        ws.status_message = "Failed to provision vector database"
        assert ws.status == "error"
        assert ws.status_message is not None
