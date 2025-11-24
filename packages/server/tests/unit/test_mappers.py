"""Unit tests for domain mappers."""

import json
from datetime import datetime

import pytest
from shared.models import ChatMessage, ChatSession, Document, User

from src.domains.chat.mappers import ChatMapper
from src.domains.documents.mappers import DocumentMapper
from src.domains.auth.mappers import UserMapper


class TestDocumentMapper:
    """Tests for DocumentMapper."""

    @pytest.fixture
    def sample_document(self) -> Document:
        """Provide a sample document."""
        return Document(
            id=1,
            user_id=100,
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="abc123",
            chunk_count=5,
            rag_collection="test_collection",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )

    def test_document_to_dto_maps_all_fields(self, sample_document: Document) -> None:
        """Test that document_to_dto maps all required fields."""
        dto = DocumentMapper.document_to_dto(sample_document)

        assert dto.id == sample_document.id
        assert dto.filename == sample_document.filename
        assert dto.file_size == sample_document.file_size
        assert dto.mime_type == sample_document.mime_type
        assert dto.chunk_count == sample_document.chunk_count
        assert dto.created_at == sample_document.created_at

    def test_document_to_dto_with_none_chunk_count(self) -> None:
        """Test mapping document with None chunk_count."""
        document = Document(
            id=1,
            user_id=100,
            filename="test.txt",
            file_path="/path/to/test.txt",
            file_size=512,
            mime_type="text/plain",
            content_hash="xyz789",
            chunk_count=None,
            rag_collection=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        dto = DocumentMapper.document_to_dto(document)

        assert dto.chunk_count is None

    def test_documents_to_dtos_empty_list(self) -> None:
        """Test mapping empty list of documents."""
        dtos = DocumentMapper.documents_to_dtos([])
        assert dtos == []

    def test_documents_to_dtos_multiple_documents(self, sample_document: Document) -> None:
        """Test mapping multiple documents."""
        document2 = Document(
            id=2,
            user_id=100,
            filename="test2.pdf",
            file_path="/path/to/test2.pdf",
            file_size=2048,
            mime_type="application/pdf",
            content_hash="def456",
            chunk_count=10,
            rag_collection="test_collection",
            created_at=datetime(2024, 1, 2),
            updated_at=datetime(2024, 1, 2),
        )

        dtos = DocumentMapper.documents_to_dtos([sample_document, document2])

        assert len(dtos) == 2
        assert dtos[0].id == 1
        assert dtos[1].id == 2
        assert dtos[0].filename == "test.pdf"
        assert dtos[1].filename == "test2.pdf"


class TestChatMapper:
    """Tests for ChatMapper."""

    @pytest.fixture
    def sample_session(self) -> ChatSession:
        """Provide a sample chat session."""
        return ChatSession(
            id=1,
            user_id=100,
            title="Test Chat",
            rag_type="vector",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 13, 0, 0),
        )

    @pytest.fixture
    def sample_message(self) -> ChatMessage:
        """Provide a sample chat message."""
        return ChatMessage(
            id=1,
            session_id=10,
            role="user",
            content="Hello, world!",
            extra_metadata=None,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

    def test_session_to_dto_maps_all_fields(self, sample_session: ChatSession) -> None:
        """Test that session_to_dto maps all required fields."""
        dto = ChatMapper.session_to_dto(sample_session)

        assert dto.id == sample_session.id
        assert dto.title == sample_session.title
        assert dto.rag_type == sample_session.rag_type
        assert dto.created_at == sample_session.created_at
        assert dto.updated_at == sample_session.updated_at

    def test_session_to_dto_with_none_title(self) -> None:
        """Test mapping session with None title."""
        session = ChatSession(
            id=1,
            user_id=100,
            title=None,
            rag_type="vector",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        dto = ChatMapper.session_to_dto(session)

        assert dto.title == "Untitled Session"

    def test_sessions_to_dtos_empty_list(self) -> None:
        """Test mapping empty list of sessions."""
        dtos = ChatMapper.sessions_to_dtos([])
        assert dtos == []

    def test_sessions_to_dtos_multiple_sessions(self, sample_session: ChatSession) -> None:
        """Test mapping multiple sessions."""
        session2 = ChatSession(
            id=2,
            user_id=100,
            title="Another Chat",
            rag_type="graph",
            created_at=datetime(2024, 1, 2),
            updated_at=datetime(2024, 1, 2),
        )

        dtos = ChatMapper.sessions_to_dtos([sample_session, session2])

        assert len(dtos) == 2
        assert dtos[0].id == 1
        assert dtos[1].id == 2
        assert dtos[0].rag_type == "vector"
        assert dtos[1].rag_type == "graph"

    def test_message_to_dto_maps_all_fields(self, sample_message: ChatMessage) -> None:
        """Test that message_to_dto maps all required fields."""
        dto = ChatMapper.message_to_dto(sample_message)

        assert dto.id == sample_message.id
        assert dto.role == sample_message.role
        assert dto.content == sample_message.content
        assert dto.created_at == sample_message.created_at

    def test_message_to_dto_with_metadata(self) -> None:
        """Test mapping message with metadata."""
        metadata = {"key": "value", "count": 5}
        message = ChatMessage(
            id=1,
            session_id=10,
            role="assistant",
            content="Response",
            extra_metadata=json.dumps(metadata),
            created_at=datetime(2024, 1, 1),
        )

        dto = ChatMapper.message_to_dto(message)

        assert dto.metadata is not None
        assert dto.metadata["key"] == "value"
        assert dto.metadata["count"] == 5

    def test_message_to_dto_without_metadata(self, sample_message: ChatMessage) -> None:
        """Test mapping message without metadata."""
        dto = ChatMapper.message_to_dto(sample_message)
        assert dto.metadata is None

    def test_messages_to_dtos_empty_list(self) -> None:
        """Test mapping empty list of messages."""
        dtos = ChatMapper.messages_to_dtos([])
        assert dtos == []

    def test_messages_to_dtos_multiple_messages(self, sample_message: ChatMessage) -> None:
        """Test mapping multiple messages."""
        message2 = ChatMessage(
            id=2,
            session_id=10,
            role="assistant",
            content="Hello back!",
            extra_metadata=None,
            created_at=datetime(2024, 1, 1, 12, 1, 0),
        )

        dtos = ChatMapper.messages_to_dtos([sample_message, message2])

        assert len(dtos) == 2
        assert dtos[0].id == 1
        assert dtos[1].id == 2
        assert dtos[0].role == "user"
        assert dtos[1].role == "assistant"


class TestUserMapper:
    """Tests for UserMapper."""

    @pytest.fixture
    def sample_user(self) -> User:
        """Provide a sample user."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            id=1,
            full_name="Test User",
        )
        user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        return user

    def test_user_to_dict_maps_all_fields(self, sample_user: User) -> None:
        """Test that user_to_dict maps all required fields."""
        result = UserMapper.user_to_dict(sample_user)

        assert result["id"] == sample_user.id
        assert result["username"] == sample_user.username
        assert result["email"] == sample_user.email
        assert result["full_name"] == sample_user.full_name
        assert result["created_at"] == sample_user.created_at.isoformat()

    def test_user_to_dict_with_none_full_name(self) -> None:
        """Test mapping user with None full_name."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            id=1,
            full_name=None,
        )
        user.created_at = datetime(2024, 1, 1)

        result = UserMapper.user_to_dict(user)

        assert result["full_name"] == ""

    def test_user_to_dict_returns_dict(self, sample_user: User) -> None:
        """Test that user_to_dict returns a dictionary."""
        result = UserMapper.user_to_dict(sample_user)
        assert isinstance(result, dict)

    def test_user_to_dict_datetime_formatted(self, sample_user: User) -> None:
        """Test that datetime is properly formatted as ISO string."""
        result = UserMapper.user_to_dict(sample_user)
        assert isinstance(result["created_at"], str)
        assert "T" in result["created_at"]

    def test_users_to_dicts_empty_list(self) -> None:
        """Test mapping empty list of users."""
        dicts = UserMapper.users_to_dicts([])
        assert dicts == []

    def test_users_to_dicts_multiple_users(self, sample_user: User) -> None:
        """Test mapping multiple users."""
        user2 = User(
            username="anotheruser",
            email="another@example.com",
            password_hash="hashed_password",
            id=2,
            full_name="Another User",
        )
        user2.created_at = datetime(2024, 1, 2)

        dicts = UserMapper.users_to_dicts([sample_user, user2])

        assert len(dicts) == 2
        assert dicts[0]["id"] == 1
        assert dicts[1]["id"] == 2
        assert dicts[0]["username"] == "testuser"
        assert dicts[1]["username"] == "anotheruser"

    def test_users_to_dicts_all_are_dicts(self, sample_user: User) -> None:
        """Test that all items in result are dictionaries."""
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash="hashed_password",
            id=2,
            full_name="User Two",
        )
        user2.created_at = datetime(2024, 1, 2)

        dicts = UserMapper.users_to_dicts([sample_user, user2])

        for item in dicts:
            assert isinstance(item, dict)
            assert "id" in item
            assert "username" in item
            assert "email" in item


class TestMapperEdgeCases:
    """Tests for mapper edge cases and data integrity."""

    def test_document_mapper_preserves_datetime(self) -> None:
        """Test that DocumentMapper preserves datetime objects."""
        created_at = datetime(2024, 1, 1, 12, 30, 45)
        document = Document(
            id=1,
            user_id=1,
            filename="test.pdf",
            file_path="/path",
            file_size=100,
            mime_type="application/pdf",
            content_hash="hash",
            chunk_count=None,
            rag_collection=None,
            created_at=created_at,
            updated_at=created_at,
        )

        dto = DocumentMapper.document_to_dto(document)

        assert dto.created_at == created_at
        assert isinstance(dto.created_at, datetime)

    def test_chat_mapper_handles_special_characters_in_metadata(self) -> None:
        """Test that ChatMapper handles special characters in metadata."""
        metadata_with_special_chars = {
            "key": "value with quotes: ' and \"",
            "special": "chars: <>&",
        }
        message = ChatMessage(
            id=1,
            session_id=1,
            role="user",
            content="Test",
            extra_metadata=json.dumps(metadata_with_special_chars),
            created_at=datetime(2024, 1, 1),
        )

        dto = ChatMapper.message_to_dto(message)

        assert dto.metadata is not None
        assert dto.metadata["key"] == "value with quotes: ' and \""
        assert dto.metadata["special"] == "chars: <>&"

    def test_user_mapper_handles_long_names(self) -> None:
        """Test that UserMapper handles long names correctly."""
        long_name = "A" * 1000
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            id=1,
            full_name=long_name,
        )
        user.created_at = datetime(2024, 1, 1)

        result = UserMapper.user_to_dict(user)

        assert result["full_name"] == long_name
        assert isinstance(result["full_name"], str)
        assert len(result["full_name"]) == 1000

    def test_chat_mapper_handles_invalid_json_metadata(self) -> None:
        """Test that ChatMapper handles invalid JSON gracefully."""
        message = ChatMessage(
            id=1,
            session_id=1,
            role="user",
            content="Test",
            extra_metadata="invalid json {",
            created_at=datetime(2024, 1, 1),
        )

        with pytest.raises(json.JSONDecodeError):
            ChatMapper.message_to_dto(message)
