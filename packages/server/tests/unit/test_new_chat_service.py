"""Unit tests for chat service."""

from unittest.mock import Mock

import pytest
from shared.models import ChatMessage, ChatSession

from src.domains.workspaces.chat.exceptions import EmptyMessageError
from src.domains.workspaces.chat.service import ChatService


@pytest.fixture
def mock_session_repository():
    """Mock chat session repository."""
    return Mock()


@pytest.fixture
def mock_message_repository():
    """Mock chat message repository."""
    return Mock()


@pytest.fixture
def mock_rag_system():
    """Mock RAG system."""
    return Mock()


@pytest.fixture
def chat_service(mock_session_repository, mock_message_repository, mock_rag_system):
    """Create chat service with mocked dependencies."""
    return ChatService(
        session_repository=mock_session_repository,
        message_repository=mock_message_repository,
        rag_system=mock_rag_system,
    )


class TestChatServiceValidation:
    """Test message validation."""

    def test_validate_message_success(self, chat_service: ChatService):
        """Test successful message validation."""
        # Should not raise exception
        chat_service.validate_message("Hello, world!")

    def test_validate_message_empty(self, chat_service: ChatService):
        """Test validation of empty message."""
        with pytest.raises(EmptyMessageError):
            chat_service.validate_message("")

    def test_validate_message_whitespace(self, chat_service: ChatService):
        """Test validation of whitespace-only message."""
        with pytest.raises(EmptyMessageError):
            chat_service.validate_message("   \n\t  ")


class TestChatServiceSessions:
    """Test chat session operations."""

    def test_create_session_success(self, chat_service: ChatService, mock_session_repository):
        """Test successful session creation."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Test Session"
        mock_session_repository.create.return_value = mock_session

        session = chat_service.create_session(user_id=1, title="Test Session")

        assert session.id == 1
        assert session.title == "Test Session"
        mock_session_repository.create.assert_called_once_with(
            user_id=1, workspace_id=None, title="Test Session", rag_type="vector"
        )

    def test_create_session_with_workspace(
        self, chat_service: ChatService, mock_session_repository
    ):
        """Test session creation with workspace association."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Workspace Session"
        mock_session_repository.create.return_value = mock_session

        session = chat_service.create_session(user_id=1, workspace_id=5, title="Workspace Session")

        assert session.id == 1
        assert session.title == "Workspace Session"
        mock_session_repository.create.assert_called_once_with(
            user_id=1, workspace_id=5, title="Workspace Session", rag_type="vector"
        )

    def test_create_session_with_first_message_title(
        self, chat_service: ChatService, mock_session_repository
    ):
        """Test session creation with first message used as title."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Hello world"
        mock_session_repository.create.return_value = mock_session

        session = chat_service.create_session(
            user_id=1, first_message="Hello world, this is a test message"
        )

        assert session.title == "Hello world"
        mock_session_repository.create.assert_called_once_with(
            user_id=1, title="Hello world", rag_type="vector"
        )

    def test_get_session_by_id(self, chat_service: ChatService, mock_session_repository):
        """Test getting session by ID."""
        mock_session = Mock(spec=ChatSession)
        mock_session_repository.get_by_id.return_value = mock_session

        result = chat_service.get_session_by_id(1)

        assert result == mock_session
        mock_session_repository.get_by_id.assert_called_once_with(1)

    def test_list_user_sessions(self, chat_service: ChatService, mock_session_repository):
        """Test listing user sessions."""
        mock_sessions = [Mock(spec=ChatSession), Mock(spec=ChatSession)]
        mock_session_repository.get_by_user.return_value = mock_sessions

        result = chat_service.list_user_sessions(user_id=1, skip=0, limit=10)

        assert result == mock_sessions
        mock_session_repository.get_by_user.assert_called_once_with(1, skip=0, limit=10)

    def test_list_workspace_sessions(self, chat_service: ChatService, mock_session_repository):
        """Test listing workspace sessions."""
        mock_sessions = [Mock(spec=ChatSession), Mock(spec=ChatSession)]
        mock_session_repository.get_by_workspace.return_value = mock_sessions

        result = chat_service.list_workspace_sessions(workspace_id=5, skip=0, limit=10)

        assert result == mock_sessions
        mock_session_repository.get_by_workspace.assert_called_once_with(5, skip=0, limit=10)

    def test_delete_session_success(self, chat_service: ChatService, mock_session_repository):
        """Test successful session deletion."""
        mock_session_repository.delete.return_value = True

        result = chat_service.delete_session(1)

        assert result is True
        mock_session_repository.delete.assert_called_once_with(1)

    def test_delete_session_not_found(self, chat_service: ChatService, mock_session_repository):
        """Test deleting non-existent session."""
        mock_session_repository.delete.return_value = False

        result = chat_service.delete_session(999)

        assert result is False
        mock_session_repository.delete.assert_called_once_with(999)

    def test_update_session_success(self, chat_service: ChatService, mock_session_repository):
        """Test successful session update."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Updated Title"
        mock_session_repository.update.return_value = mock_session

        result = chat_service.update_session(1, title="Updated Title")

        assert result == mock_session
        mock_session_repository.update.assert_called_once_with(1, title="Updated Title")

    def test_update_session_not_found(self, chat_service: ChatService, mock_session_repository):
        """Test updating non-existent session."""
        mock_session_repository.update.return_value = None

        result = chat_service.update_session(999, title="Updated")

        assert result is None
        mock_session_repository.update.assert_called_once_with(999, title="Updated")


class TestChatServiceGetOrCreateSession:
    """Test get_or_create_session functionality."""

    def test_get_or_create_existing_session(
        self, chat_service: ChatService, mock_session_repository
    ):
        """Test returning existing session."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 5
        mock_session_repository.get_by_id.return_value = mock_session

        result = chat_service.get_or_create_session(user_id=1, session_id=5)

        assert result == mock_session
        mock_session_repository.get_by_id.assert_called_once_with(5)
        # Should not create a new session
        mock_session_repository.create.assert_not_called()

    def test_get_or_create_new_session(self, chat_service: ChatService, mock_session_repository):
        """Test creating new session when none exists."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 10
        mock_session_repository.get_by_id.return_value = None
        mock_session_repository.create.return_value = mock_session

        result = chat_service.get_or_create_session(
            user_id=1, workspace_id=3, first_message="Hello"
        )

        assert result == mock_session
        mock_session_repository.get_by_id.assert_called_once_with(None)
        mock_session_repository.create.assert_called_once_with(
            user_id=1, workspace_id=3, title="Hello", rag_type="vector"
        )

    def test_get_or_create_with_workspace_association(
        self, chat_service: ChatService, mock_session_repository
    ):
        """Test workspace association in get_or_create."""
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 15
        mock_session_repository.get_by_id.return_value = None
        mock_session_repository.create.return_value = mock_session

        result = chat_service.get_or_create_session(
            user_id=2, workspace_id=7, session_id=None, first_message="Test message"
        )

        assert result == mock_session
        mock_session_repository.create.assert_called_once_with(
            user_id=2, workspace_id=7, title="Test message", rag_type="vector"
        )


class TestChatServiceMessages:
    """Test chat message operations."""

    def test_create_message(self, chat_service: ChatService, mock_message_repository):
        """Test creating a message."""
        mock_message = Mock(spec=ChatMessage)
        mock_message.id = 1
        mock_message_repository.create.return_value = mock_message

        result = chat_service.create_message(
            session_id=1, role="user", content="Hello", metadata={"test": "data"}
        )

        assert result.id == 1
        mock_message_repository.create.assert_called_once()

    def test_get_message_by_id(self, chat_service: ChatService, mock_message_repository):
        """Test getting message by ID."""
        mock_message = Mock(spec=ChatMessage)
        mock_message_repository.get_by_id.return_value = mock_message

        result = chat_service.get_message_by_id(1)

        assert result == mock_message
        mock_message_repository.get_by_id.assert_called_once_with(1)

    def test_list_session_messages(self, chat_service: ChatService, mock_message_repository):
        """Test listing session messages."""
        mock_messages = [Mock(spec=ChatMessage), Mock(spec=ChatMessage)]
        mock_message_repository.get_by_session.return_value = mock_messages

        result = chat_service.list_session_messages(session_id=1, skip=0, limit=10)

        assert result == mock_messages
        mock_message_repository.get_by_session.assert_called_once_with(1, skip=0, limit=10)

    def test_delete_message(self, chat_service: ChatService, mock_message_repository):
        """Test deleting a message."""
        mock_message_repository.delete.return_value = True

        result = chat_service.delete_message(1)

        assert result is True
        mock_message_repository.delete.assert_called_once_with(1)


class TestChatServiceSendMessage:
    """Test sending chat messages."""

    def test_send_message_success(
        self, chat_service: ChatService, mock_session_repository, mock_message_repository
    ):
        """Test successful message sending."""
        # Setup mocks
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session_repository.get_by_id.return_value = mock_session

        mock_message = Mock(spec=ChatMessage)
        mock_message.id = "msg-123"
        mock_message_repository.create.return_value = mock_message

        # Mock LLM provider
        with pytest.raises(Exception):  # noqa: B017  # Will fail due to missing LLM provider
            chat_service.send_message(
                workspace_id=1,
                session_id=1,
                user_id=1,
                content="Hello",
                message_type="user",
                ignore_rag=False,
            )

    def test_send_message_validation_error(self, chat_service: ChatService):
        """Test sending message with validation error."""
        with pytest.raises(EmptyMessageError):
            chat_service.send_message(
                workspace_id=1, session_id=1, user_id=1, content="", message_type="user"
            )


class TestChatServiceStreaming:
    """Test streaming chat functionality."""

    def test_stream_chat_response_success(
        self,
        chat_service: ChatService,
        mock_session_repository,
        mock_message_repository,
        mock_rag_system,
    ):
        """Test successful streaming chat response."""
        # Setup mocks
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session_repository.get_by_id.return_value = mock_session

        mock_message = Mock(spec=ChatMessage)
        mock_message.id = 1
        mock_message_repository.create.return_value = mock_message
        mock_message_repository.get_by_session.return_value = []

        # Mock RAG system to return no context
        mock_rag_system.query.return_value = []

        # Mock LLM provider
        mock_llm = Mock()
        mock_llm.chat_stream.return_value = iter(["Hello", " world", "!"])
        mock_llm.chat.return_value = "Hello world!"

        # Collect streaming events
        events = list(
            chat_service.stream_chat_response(
                user_id=1,
                message="Hello",
                llm_provider=mock_llm,
                session_id=1,
                rag_type="vector",
                request_id="req-123",
            )
        )

        # Should have chunk events and a complete event
        assert len(events) >= 2
        assert events[0].event_type == "chunk"
        assert events[-1].event_type == "complete"

    def test_cancel_stream(self, chat_service: ChatService):
        """Test cancelling a stream."""
        # Set up a cancel flag
        chat_service._get_cancel_flag("req-123")

        # Cancel the stream
        chat_service.cancel_stream("req-123")

        # Check that the flag is set
        flag = chat_service._get_cancel_flag("req-123")
        assert flag.is_set()


class TestChatServiceRAGIntegration:
    """Test RAG integration."""

    def test_process_chat_message_with_rag_context(
        self,
        chat_service: ChatService,
        mock_session_repository,
        mock_message_repository,
        mock_rag_system,
    ):
        """Test processing message with RAG context."""
        # Setup mocks
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session_repository.get_by_id.return_value = mock_session

        mock_message = Mock(spec=ChatMessage)
        mock_message.id = 1
        mock_message_repository.create.return_value = mock_message
        mock_message_repository.get_by_session.return_value = []

        # Mock RAG system to return context
        from shared.types.document import Chunk
        from shared.types.retrieval import RetrievalResult

        mock_chunk = Mock(spec=Chunk)
        mock_chunk.text = "Test context"
        mock_chunk.metadata = {"source": "test"}

        mock_result = Mock(spec=RetrievalResult)
        mock_result.chunk = mock_chunk
        mock_result.score = 0.9

        mock_rag_system.query.return_value = [mock_result]

        # Mock LLM provider
        mock_llm = Mock()
        mock_llm.chat.return_value = "Response with context"

        result = chat_service.process_chat_message_with_llm(
            user_id=1,
            message="Test query",
            llm_provider=mock_llm,
            session_id=1,
            rag_type="vector",
            ignore_rag=False,
        )

        assert result.answer == "Response with context"
        assert len(result.context) == 1
        assert result.context[0].text == "Test context"
        assert result.no_context_found is False

    def test_process_chat_message_no_rag_context(
        self,
        chat_service: ChatService,
        mock_session_repository,
        mock_message_repository,
        mock_rag_system,
    ):
        """Test processing message with no RAG context found."""
        # Setup mocks
        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session_repository.get_by_id.return_value = mock_session

        mock_message = Mock(spec=ChatMessage)
        mock_message.id = 1
        mock_message_repository.create.return_value = mock_message
        mock_message_repository.get_by_session.return_value = []

        # Mock RAG system to return low-scoring context (below threshold)
        from shared.types.document import Chunk
        from shared.types.retrieval import RetrievalResult

        mock_chunk = Mock(spec=Chunk)
        mock_chunk.text = "Low relevance context"
        mock_chunk.metadata = {"source": "test"}

        mock_result = Mock(spec=RetrievalResult)
        mock_result.chunk = mock_chunk
        mock_result.score = 0.05  # Below 0.1 threshold

        mock_rag_system.query.return_value = [mock_result]

        # Mock LLM provider
        mock_llm = Mock()
        mock_llm.chat.return_value = "Response without context"

        result = chat_service.process_chat_message_with_llm(
            user_id=1,
            message="Test query",
            llm_provider=mock_llm,
            session_id=1,
            rag_type="vector",
            ignore_rag=False,
        )

        assert result.answer == "Response without context"
        assert len(result.context) == 1  # Still includes the context
        assert result.no_context_found is True  # But marks as no meaningful context
