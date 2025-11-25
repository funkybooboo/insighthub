"""Unit tests for chat orchestrator worker."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from packages.workers.chat.src.main import ChatOrchestratorWorker


@pytest.fixture
def mock_rabbitmq_connection():
    """Mock RabbitMQ connection."""
    return Mock()


@pytest.fixture
def mock_channel():
    """Mock RabbitMQ channel."""
    return Mock()


@pytest.fixture
def chat_worker(mock_rabbitmq_connection, mock_channel):
    """Create chat worker with mocked dependencies."""
    with patch('packages.workers.chat.src.main.pika') as mock_pika:
        mock_pika.BlockingConnection.return_value = mock_rabbitmq_connection
        mock_rabbitmq_connection.channel.return_value = mock_channel

        worker = ChatOrchestratorWorker()
        # Mock the initialization methods
        worker._rag_system = Mock()
        worker._llm_provider = Mock()
        return worker


class TestChatOrchestratorWorkerInitialization:
    """Test worker initialization."""

    def test_worker_initialization(self, chat_worker):
        """Test that worker initializes with correct parameters."""
        assert chat_worker._rabbitmq_url == "amqp://insighthub:insighthub_dev@rabbitmq:5672/"
        assert chat_worker._exchange == "insighthub"
        assert chat_worker._consume_routing_key == "chat.message_received"
        assert chat_worker._consume_queue == "chat.message_received"

    def test_rag_system_initialization(self, chat_worker):
        """Test RAG system initialization."""
        with patch('packages.workers.chat.src.main.create_vector_database') as mock_create_vector_db, \
             patch('packages.workers.chat.src.main.create_embedding_encoder') as mock_create_encoder, \
             patch('packages.workers.chat.src.main.VectorRAG') as mock_vector_rag:

            mock_db = Mock()
            mock_encoder = Mock()
            mock_rag = Mock()

            mock_create_vector_db.return_value = mock_db
            mock_create_encoder.return_value = mock_encoder
            mock_vector_rag.return_value = mock_rag

            chat_worker._init_rag_system()

            assert chat_worker._rag_system == mock_rag
            mock_create_vector_db.assert_called_once()
            mock_create_encoder.assert_called_once()
            mock_vector_rag.assert_called_once_with(embedder=mock_encoder, vector_store=mock_db)

    def test_rag_system_initialization_failure(self, chat_worker):
        """Test RAG system initialization failure."""
        with patch('packages.workers.chat.src.main.create_vector_database') as mock_create_vector_db:
            mock_create_vector_db.return_value = None

            chat_worker._init_rag_system()

            assert chat_worker._rag_system is None

    def test_llm_provider_initialization(self, chat_worker):
        """Test LLM provider initialization."""
        with patch('packages.workers.chat.src.main.create_llm_provider') as mock_create_llm:
            mock_llm = Mock()
            mock_create_llm.return_value = mock_llm

            chat_worker._init_llm_provider()

            assert chat_worker._llm_provider == mock_llm
            mock_create_llm.assert_called_once()


class TestChatOrchestratorWorkerProcessing:
    """Test chat message processing."""

    def test_process_event_success(self, chat_worker):
        """Test successful event processing."""
        # Setup mocks
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        # Mock RAG query
        mock_result = Mock()
        mock_result.chunk.text = "Test context"
        mock_result.chunk.metadata = {"source": "test"}
        mock_result.score = 0.9
        chat_worker._rag_system.query.return_value = [mock_result]

        # Mock LLM streaming
        chat_worker._llm_provider.chat_stream.return_value = iter(["Hello", " world", "!"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello, how are you?",
            "message_type": "user",
            "ignore_rag": False,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Verify RAG was called
        chat_worker._rag_system.query.assert_called_once_with("Hello, how are you?", top_k=8)

        # Verify LLM was called with enhanced context
        chat_worker._llm_provider.chat_stream.assert_called_once()

        # Verify events were published (checking publish_event calls)
        assert chat_worker.publish_event.call_count >= 1  # At least response_complete

    def test_process_event_no_rag_context(self, chat_worker):
        """Test processing when no RAG context is found."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        # Mock empty RAG results
        chat_worker._rag_system.query.return_value = []
        chat_worker._llm_provider.chat_stream.return_value = iter(["Response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello?",
            "message_type": "user",
            "ignore_rag": False,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit no_context_found event
        chat_worker.publish_event.assert_any_call(
            "chat.no_context_found",
            {
                "session_id": 1,
                "message_id": "msg-123",
                "request_id": "chat-1-msg-123",
                "query": "Hello?"
            }
        )

    def test_process_event_ignore_rag(self, chat_worker):
        """Test processing when RAG is ignored."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        chat_worker._llm_provider.chat_stream.return_value = iter(["Response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello!",
            "message_type": "user",
            "ignore_rag": True,  # Ignore RAG
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should not call RAG
        chat_worker._rag_system.query.assert_not_called()

        # Should still process LLM
        chat_worker._llm_provider.chat_stream.assert_called_once()

    def test_process_event_low_relevance_context(self, chat_worker):
        """Test processing with low-relevance RAG context."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        # Mock low-relevance results (score < 0.1)
        mock_result = Mock()
        mock_result.chunk.text = "Irrelevant context"
        mock_result.chunk.metadata = {"source": "test"}
        mock_result.score = 0.05  # Below threshold
        chat_worker._rag_system.query.return_value = [mock_result]

        chat_worker._llm_provider.chat_stream.return_value = iter(["Response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello?",
            "message_type": "user",
            "ignore_rag": False,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit no_context_found since meaningful context threshold not met
        chat_worker.publish_event.assert_any_call(
            "chat.no_context_found",
            {
                "session_id": 1,
                "message_id": "msg-123",
                "request_id": "chat-1-msg-123",
                "query": "Hello?"
            }
        )

    def test_process_event_llm_error(self, chat_worker):
        """Test handling of LLM processing errors."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        chat_worker._rag_system.query.return_value = []
        chat_worker._llm_provider.chat_stream.side_effect = Exception("LLM Error")

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello?",
            "message_type": "user",
            "ignore_rag": True,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit error event
        chat_worker.publish_event.assert_any_call(
            "chat.error",
            {
                "session_id": 1,
                "message_id": "msg-123",
                "request_id": "chat-1-msg-123",
                "error": "LLM Error"
            }
        )

    def test_process_event_rag_error(self, chat_worker):
        """Test handling of RAG retrieval errors."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        chat_worker._rag_system.query.side_effect = Exception("RAG Error")
        chat_worker._llm_provider.chat_stream.return_value = iter(["Response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello?",
            "message_type": "user",
            "ignore_rag": False,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should continue processing despite RAG error
        chat_worker._llm_provider.chat_stream.assert_called_once()

    def test_process_event_streaming_chunks(self, chat_worker):
        """Test that streaming chunks are properly emitted."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        chat_worker._rag_system.query.return_value = []
        chat_worker._llm_provider.chat_stream.return_value = iter(["Hello", " ", "world", "!"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello world",
            "message_type": "user",
            "ignore_rag": True,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit chunk events for each piece
        chunk_calls = [call for call in chat_worker.publish_event.call_args_list
                      if call[0][0] == "chat.response_chunk"]

        assert len(chunk_calls) == 4  # 4 chunks: "Hello", " ", "world", "!"

        # Verify chunk event structure
        for call in chunk_calls:
            event_name, event_data = call[0], call[1]
            assert "session_id" in event_data
            assert "message_id" in event_data
            assert "request_id" in event_data
            assert "chunk" in event_data

    def test_process_event_completion(self, chat_worker):
        """Test that completion event is emitted."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = Mock()

        chat_worker._rag_system.query.return_value = []
        chat_worker._llm_provider.chat_stream.return_value = iter(["Final", " response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello",
            "message_type": "user",
            "ignore_rag": True,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit completion event
        chat_worker.publish_event.assert_any_call(
            "chat.response_complete",
            {
                "session_id": 1,
                "message_id": "msg-123",
                "request_id": "chat-1-msg-123",
                "full_response": "Final response"
            }
        )


class TestChatOrchestratorWorkerFallback:
    """Test fallback behavior when components are unavailable."""

    def test_process_event_no_rag_system(self, chat_worker):
        """Test processing when RAG system is not available."""
        chat_worker._rag_system = None  # Not initialized
        chat_worker._llm_provider = Mock()
        chat_worker._llm_provider.chat_stream.return_value = iter(["Response"])

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello",
            "message_type": "user",
            "ignore_rag": False,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should still process without RAG
        chat_worker._llm_provider.chat_stream.assert_called_once()

    def test_process_event_no_llm_provider(self, chat_worker):
        """Test error handling when LLM provider is not available."""
        chat_worker._rag_system = Mock()
        chat_worker._llm_provider = None  # Not initialized

        event_data = {
            "message_id": "msg-123",
            "session_id": 1,
            "workspace_id": 1,
            "user_id": 1,
            "content": "Hello",
            "message_type": "user",
            "ignore_rag": True,
            "request_id": "chat-1-msg-123"
        }

        chat_worker.process_event(event_data)

        # Should emit error event
        chat_worker.publish_event.assert_any_call(
            "chat.error",
            {
                "session_id": 1,
                "message_id": "msg-123",
                "request_id": "chat-1-msg-123",
                "error": "LLM provider not available"
            }
        )