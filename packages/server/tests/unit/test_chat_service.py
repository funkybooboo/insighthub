"""Unit tests for ChatService."""

import json
from collections.abc import Generator
from datetime import datetime

import pytest

from src.domains.chat.exceptions import EmptyMessageError
from src.domains.chat.models import ChatMessage, ChatSession
from src.domains.chat.repositories import ChatMessageRepository, ChatSessionRepository
from src.domains.chat.service import ChatService
from src.infrastructure.llm.llm import LlmProvider


class DummyLlmProvider(LlmProvider):
    """Dummy LLM provider for testing."""

    def __init__(self, response: str = "Dummy response") -> None:
        """Initialize with a fixed response."""
        self.response = response
        self.model_name = "dummy-model"

    def generate_response(self, prompt: str) -> str:
        """Return fixed response."""
        return self.response

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """Return fixed response for chat."""
        return f"Response to: {message}"

    def chat_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> Generator[str, None, None]:
        """Stream fixed response in chunks."""
        words = self.response.split()
        for word in words:
            yield word + " "

    def health_check(self) -> dict[str, str | bool]:
        """Return healthy status."""
        return {"status": "healthy", "provider": "dummy"}

    def get_model_name(self) -> str:
        """Get model name."""
        return self.model_name


class FakeChatSessionRepository(ChatSessionRepository):
    """Fake chat session repository for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.sessions: dict[int, ChatSession] = {}
        self.next_id = 1

    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            id=self.next_id,
            user_id=user_id,
            title=title or f"Session {self.next_id}",
            rag_type=rag_type or "vector",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.sessions[session.id] = session
        self.next_id += 1
        return session

    def get_by_id(self, session_id: int) -> ChatSession | None:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ChatSession]:
        """Get all sessions for a user."""
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        return user_sessions[skip : skip + limit]

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ChatSession]:
        """Get all sessions."""
        all_sessions = list(self.sessions.values())
        return all_sessions[skip : skip + limit]

    def update(self, session_id: int, **kwargs: str) -> ChatSession | None:
        """Update session fields."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        return session

    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


class FakeChatMessageRepository(ChatMessageRepository):
    """Fake chat message repository for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.messages: dict[int, ChatMessage] = {}
        self.next_id = 1

    def create(
        self, session_id: int, role: str, content: str, extra_metadata: str | None = None
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            id=self.next_id,
            session_id=session_id,
            role=role,
            content=content,
            extra_metadata=extra_metadata,
            created_at=datetime.now(),
        )
        self.messages[message.id] = message
        self.next_id += 1
        return message

    def get_by_id(self, message_id: int) -> ChatMessage | None:
        """Get message by ID."""
        return self.messages.get(message_id)

    def get_by_session(self, session_id: int, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        """Get all messages for a session."""
        session_messages = [m for m in self.messages.values() if m.session_id == session_id]
        return session_messages[skip : skip + limit]

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        """Get all messages."""
        all_messages = list(self.messages.values())
        return all_messages[skip : skip + limit]

    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        if message_id in self.messages:
            del self.messages[message_id]
            return True
        return False


@pytest.fixture
def fake_session_repository() -> FakeChatSessionRepository:
    """Provide a fake session repository."""
    return FakeChatSessionRepository()


@pytest.fixture
def fake_message_repository() -> FakeChatMessageRepository:
    """Provide a fake message repository."""
    return FakeChatMessageRepository()


@pytest.fixture
def service(
    fake_session_repository: FakeChatSessionRepository,
    fake_message_repository: FakeChatMessageRepository,
) -> ChatService:
    """Provide a ChatService with fake repositories."""
    return ChatService(
        session_repository=fake_session_repository, message_repository=fake_message_repository
    )


@pytest.fixture
def dummy_llm() -> DummyLlmProvider:
    """Provide a dummy LLM provider."""
    return DummyLlmProvider("This is a dummy response")


class TestMessageValidation:
    """Tests for message validation."""

    def test_validate_message_success(self, service: ChatService) -> None:
        """Test validating a valid message."""
        service.validate_message("Hello, world!")

    def test_validate_empty_message(self, service: ChatService) -> None:
        """Test validating empty message."""
        with pytest.raises(EmptyMessageError):
            service.validate_message("")

    def test_validate_whitespace_message(self, service: ChatService) -> None:
        """Test validating whitespace-only message."""
        with pytest.raises(EmptyMessageError):
            service.validate_message("   ")


class TestSessionCreation:
    """Tests for session creation."""

    def test_create_session_with_title(self, service: ChatService) -> None:
        """Test creating session with title."""
        session = service.create_session(user_id=1, title="Test Session")

        assert session.id == 1
        assert session.user_id == 1
        assert session.title == "Test Session"
        assert session.rag_type == "vector"

    def test_create_session_without_title(self, service: ChatService) -> None:
        """Test creating session without title."""
        session = service.create_session(user_id=1)

        assert session.user_id == 1
        assert session.title is not None

    def test_create_session_with_first_message(self, service: ChatService) -> None:
        """Test creating session with first message as title."""
        long_message = "This is a very long first message that should be truncated"
        session = service.create_session(user_id=1, first_message=long_message)

        assert session.title == long_message[:50] + "..."

    def test_create_session_with_short_first_message(self, service: ChatService) -> None:
        """Test creating session with short first message."""
        message = "Short message"
        session = service.create_session(user_id=1, first_message=message)

        assert session.title == message

    def test_create_session_with_custom_rag_type(self, service: ChatService) -> None:
        """Test creating session with custom RAG type."""
        session = service.create_session(user_id=1, rag_type="graph")

        assert session.rag_type == "graph"


class TestSessionRetrieval:
    """Tests for session retrieval."""

    def test_get_session_by_id(self, service: ChatService) -> None:
        """Test getting session by ID."""
        created = service.create_session(user_id=1, title="Test")
        session = service.get_session_by_id(created.id)

        assert session is not None
        assert session.id == created.id

    def test_get_session_by_id_not_found(self, service: ChatService) -> None:
        """Test getting non-existent session."""
        session = service.get_session_by_id(999)
        assert session is None

    def test_list_user_sessions_empty(self, service: ChatService) -> None:
        """Test listing sessions for user with no sessions."""
        sessions = service.list_user_sessions(user_id=1)
        assert len(sessions) == 0

    def test_list_user_sessions_multiple(self, service: ChatService) -> None:
        """Test listing multiple sessions."""
        service.create_session(user_id=1, title="Session 1")
        service.create_session(user_id=1, title="Session 2")
        service.create_session(user_id=2, title="Session 3")

        user1_sessions = service.list_user_sessions(user_id=1)
        user2_sessions = service.list_user_sessions(user_id=2)

        assert len(user1_sessions) == 2
        assert len(user2_sessions) == 1


class TestSessionUpdate:
    """Tests for session updates."""

    def test_update_session_success(self, service: ChatService) -> None:
        """Test updating session."""
        session = service.create_session(user_id=1, title="Original")
        updated = service.update_session(session.id, title="Updated")

        assert updated is not None
        assert updated.title == "Updated"

    def test_update_session_not_found(self, service: ChatService) -> None:
        """Test updating non-existent session."""
        result = service.update_session(999, title="Updated")
        assert result is None


class TestSessionDeletion:
    """Tests for session deletion."""

    def test_delete_session_success(self, service: ChatService) -> None:
        """Test deleting a session."""
        session = service.create_session(user_id=1, title="Test")
        result = service.delete_session(session.id)

        assert result is True
        assert service.get_session_by_id(session.id) is None

    def test_delete_session_not_found(self, service: ChatService) -> None:
        """Test deleting non-existent session."""
        result = service.delete_session(999)
        assert result is False


class TestMessageCreation:
    """Tests for message creation."""

    def test_create_message_success(self, service: ChatService) -> None:
        """Test creating a message."""
        session = service.create_session(user_id=1, title="Test")
        message = service.create_message(session_id=session.id, role="user", content="Hello")

        assert message.id == 1
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello"

    def test_create_message_with_metadata(self, service: ChatService) -> None:
        """Test creating message with metadata."""
        session = service.create_session(user_id=1, title="Test")
        metadata: dict[str, str | int] = {"key": "value", "count": 5}
        message = service.create_message(
            session_id=session.id, role="assistant", content="Response", metadata=metadata
        )

        assert message.extra_metadata is not None
        parsed_metadata = json.loads(message.extra_metadata)
        assert parsed_metadata["key"] == "value"
        assert parsed_metadata["count"] == 5


class TestMessageRetrieval:
    """Tests for message retrieval."""

    def test_get_message_by_id(self, service: ChatService) -> None:
        """Test getting message by ID."""
        session = service.create_session(user_id=1, title="Test")
        created = service.create_message(session_id=session.id, role="user", content="Hello")
        message = service.get_message_by_id(created.id)

        assert message is not None
        assert message.id == created.id

    def test_get_message_by_id_not_found(self, service: ChatService) -> None:
        """Test getting non-existent message."""
        message = service.get_message_by_id(999)
        assert message is None

    def test_list_session_messages_empty(self, service: ChatService) -> None:
        """Test listing messages for session with no messages."""
        session = service.create_session(user_id=1, title="Test")
        messages = service.list_session_messages(session.id)

        assert len(messages) == 0

    def test_list_session_messages_multiple(self, service: ChatService) -> None:
        """Test listing multiple messages."""
        session1 = service.create_session(user_id=1, title="Test 1")
        session2 = service.create_session(user_id=1, title="Test 2")

        service.create_message(session_id=session1.id, role="user", content="Message 1")
        service.create_message(session_id=session1.id, role="assistant", content="Response 1")
        service.create_message(session_id=session2.id, role="user", content="Message 2")

        session1_messages = service.list_session_messages(session1.id)
        session2_messages = service.list_session_messages(session2.id)

        assert len(session1_messages) == 2
        assert len(session2_messages) == 1


class TestMessageDeletion:
    """Tests for message deletion."""

    def test_delete_message_success(self, service: ChatService) -> None:
        """Test deleting a message."""
        session = service.create_session(user_id=1, title="Test")
        message = service.create_message(session_id=session.id, role="user", content="Hello")
        result = service.delete_message(message.id)

        assert result is True
        assert service.get_message_by_id(message.id) is None

    def test_delete_message_not_found(self, service: ChatService) -> None:
        """Test deleting non-existent message."""
        result = service.delete_message(999)
        assert result is False


class TestGetOrCreateSession:
    """Tests for get_or_create_session."""

    def test_get_or_create_returns_existing(self, service: ChatService) -> None:
        """Test that existing session is returned."""
        session = service.create_session(user_id=1, title="Test")
        retrieved = service.get_or_create_session(user_id=1, session_id=session.id)

        assert retrieved.id == session.id

    def test_get_or_create_creates_new(self, service: ChatService) -> None:
        """Test that new session is created if not found."""
        session = service.get_or_create_session(user_id=1)

        assert session.id is not None
        assert session.user_id == 1

    def test_get_or_create_with_first_message(self, service: ChatService) -> None:
        """Test creating new session with first message."""
        session = service.get_or_create_session(user_id=1, first_message="What is RAG?")

        assert session.title is not None
        assert "What is RAG?" in session.title


class TestProcessChatMessage:
    """Tests for process_chat_message."""

    def test_process_chat_message_creates_session(self, service: ChatService) -> None:
        """Test that processing creates a session."""
        response = service.process_chat_message(user_id=1, message="Hello")

        assert response.session_id is not None
        session = service.get_session_by_id(response.session_id)
        assert session is not None

    def test_process_chat_message_stores_messages(self, service: ChatService) -> None:
        """Test that processing stores both user and assistant messages."""
        response = service.process_chat_message(user_id=1, message="Hello")

        messages = service.list_session_messages(response.session_id)
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"

    def test_process_chat_message_with_existing_session(self, service: ChatService) -> None:
        """Test processing with existing session."""
        session = service.create_session(user_id=1, title="Test")
        response = service.process_chat_message(user_id=1, message="Hello", session_id=session.id)

        assert response.session_id == session.id


class TestProcessChatMessageWithLlm:
    """Tests for process_chat_message_with_llm."""

    def test_process_with_llm_success(
        self, service: ChatService, dummy_llm: DummyLlmProvider
    ) -> None:
        """Test processing chat with LLM."""
        response = service.process_chat_message_with_llm(
            user_id=1, message="Hello", llm_provider=dummy_llm
        )

        assert response.answer == "Response to: Hello"
        assert response.session_id is not None

    def test_process_with_llm_stores_messages(
        self, service: ChatService, dummy_llm: DummyLlmProvider
    ) -> None:
        """Test that LLM processing stores messages."""
        response = service.process_chat_message_with_llm(
            user_id=1, message="Hello", llm_provider=dummy_llm
        )

        messages = service.list_session_messages(response.session_id)
        assert len(messages) == 2

    def test_process_with_llm_uses_conversation_history(
        self, service: ChatService, dummy_llm: DummyLlmProvider
    ) -> None:
        """Test that LLM processing includes conversation history."""
        session = service.create_session(user_id=1, title="Test")
        service.create_message(session_id=session.id, role="user", content="First message")
        service.create_message(session_id=session.id, role="assistant", content="First response")

        service.process_chat_message_with_llm(
            user_id=1, message="Second message", llm_provider=dummy_llm, session_id=session.id
        )

        messages = service.list_session_messages(session.id)
        assert len(messages) == 4


class TestStreamChatResponse:
    """Tests for stream_chat_response."""

    def test_stream_chat_response_yields_chunks(
        self, service: ChatService, dummy_llm: DummyLlmProvider
    ) -> None:
        """Test that streaming yields chunks."""
        stream = service.stream_chat_response(user_id=1, message="Hello", llm_provider=dummy_llm)

        events = list(stream)
        assert len(events) > 0

        chunk_events = [e for e in events if e.event_type == "chunk"]
        complete_events = [e for e in events if e.event_type == "complete"]

        assert len(chunk_events) > 0
        assert len(complete_events) == 1

    def test_stream_chat_response_stores_messages(
        self, service: ChatService, dummy_llm: DummyLlmProvider
    ) -> None:
        """Test that streaming stores messages."""
        stream = service.stream_chat_response(user_id=1, message="Hello", llm_provider=dummy_llm)

        events = list(stream)
        complete_events = [e for e in events if e.event_type == "complete"]

        assert len(complete_events) > 0
        session_id_value = complete_events[0].data["session_id"]
        assert isinstance(session_id_value, int)

        messages = service.list_session_messages(session_id_value)
        assert len(messages) == 2
