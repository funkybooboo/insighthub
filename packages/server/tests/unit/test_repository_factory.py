"""Unit tests for repository factory."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.repositories import (
    ChatMessageRepositoryType,
    ChatSessionRepositoryType,
    DocumentRepositoryType,
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlUserRepository,
    UserRepositoryType,
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)


@pytest.fixture
def mock_db_session() -> Session:
    """Create a mock database session."""
    return MagicMock(spec=Session)


class TestUserRepositoryFactory:
    """Test cases for user repository factory."""

    def test_create_sql_repository_explicitly(self, mock_db_session: Session) -> None:
        """Test creating SQL user repository with explicit type."""
        repo = create_user_repository(mock_db_session, UserRepositoryType.SQL)

        assert isinstance(repo, SqlUserRepository)
        assert repo.db == mock_db_session

    def test_create_repository_from_config(self, mock_db_session: Session) -> None:
        """Test creating user repository from config."""
        with patch("src.config.USER_REPOSITORY_TYPE", "sql"):
            repo = create_user_repository(mock_db_session)

            assert isinstance(repo, SqlUserRepository)

    def test_invalid_repository_type_raises_error(self, mock_db_session: Session) -> None:
        """Test that invalid repository type raises ValueError."""
        with patch("src.config.USER_REPOSITORY_TYPE", "invalid_type"):
            with pytest.raises(ValueError) as exc_info:
                create_user_repository(mock_db_session)

            assert "invalid_type" in str(exc_info.value)

    def test_repository_type_enum_value(self) -> None:
        """Test that UserRepositoryType enum has expected value."""
        assert UserRepositoryType.SQL.value == "sql"


class TestDocumentRepositoryFactory:
    """Test cases for document repository factory."""

    def test_create_sql_repository_explicitly(self, mock_db_session: Session) -> None:
        """Test creating SQL document repository with explicit type."""
        repo = create_document_repository(mock_db_session, DocumentRepositoryType.SQL)

        assert isinstance(repo, SqlDocumentRepository)
        assert repo.db == mock_db_session

    def test_create_repository_from_config(self, mock_db_session: Session) -> None:
        """Test creating document repository from config."""
        with patch("src.config.DOCUMENT_REPOSITORY_TYPE", "sql"):
            repo = create_document_repository(mock_db_session)

            assert isinstance(repo, SqlDocumentRepository)

    def test_repository_type_enum_value(self) -> None:
        """Test that DocumentRepositoryType enum has expected value."""
        assert DocumentRepositoryType.SQL.value == "sql"


class TestChatSessionRepositoryFactory:
    """Test cases for chat session repository factory."""

    def test_create_sql_repository_explicitly(self, mock_db_session: Session) -> None:
        """Test creating SQL chat session repository with explicit type."""
        repo = create_chat_session_repository(
            mock_db_session, ChatSessionRepositoryType.SQL
        )

        assert isinstance(repo, SqlChatSessionRepository)
        assert repo.db == mock_db_session

    def test_create_repository_from_config(self, mock_db_session: Session) -> None:
        """Test creating chat session repository from config."""
        with patch("src.config.CHAT_SESSION_REPOSITORY_TYPE", "sql"):
            repo = create_chat_session_repository(mock_db_session)

            assert isinstance(repo, SqlChatSessionRepository)

    def test_repository_type_enum_value(self) -> None:
        """Test that ChatSessionRepositoryType enum has expected value."""
        assert ChatSessionRepositoryType.SQL.value == "sql"


class TestChatMessageRepositoryFactory:
    """Test cases for chat message repository factory."""

    def test_create_sql_repository_explicitly(self, mock_db_session: Session) -> None:
        """Test creating SQL chat message repository with explicit type."""
        repo = create_chat_message_repository(
            mock_db_session, ChatMessageRepositoryType.SQL
        )

        assert isinstance(repo, SqlChatMessageRepository)
        assert repo.db == mock_db_session

    def test_create_repository_from_config(self, mock_db_session: Session) -> None:
        """Test creating chat message repository from config."""
        with patch("src.config.CHAT_MESSAGE_REPOSITORY_TYPE", "sql"):
            repo = create_chat_message_repository(mock_db_session)

            assert isinstance(repo, SqlChatMessageRepository)

    def test_repository_type_enum_value(self) -> None:
        """Test that ChatMessageRepositoryType enum has expected value."""
        assert ChatMessageRepositoryType.SQL.value == "sql"
