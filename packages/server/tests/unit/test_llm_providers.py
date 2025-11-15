"""Unit tests for LLM providers."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.infrastructure.llm.claude_provider import ClaudeLlmProvider
from src.infrastructure.llm.ollama import OllamaLlmProvider
from src.infrastructure.llm.openai_provider import OpenAiLlmProvider


class TestOllamaLlmProvider:
    """Tests for Ollama LLM provider."""

    @pytest.fixture
    def provider(self) -> OllamaLlmProvider:
        """Create Ollama provider instance."""
        return OllamaLlmProvider(base_url="http://localhost:11434", model_name="llama3.2")

    def test_initialization(self, provider: OllamaLlmProvider) -> None:
        """Test provider initialization."""
        assert provider.base_url == "http://localhost:11434"
        assert provider.model_name == "llama3.2"

    def test_get_model_name(self, provider: OllamaLlmProvider) -> None:
        """Test getting model name."""
        assert provider.get_model_name() == "llama3.2"

    @patch("requests.post")
    def test_generate_response_success(
        self, mock_post: MagicMock, provider: OllamaLlmProvider
    ) -> None:
        """Test successful response generation."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "This is a test response"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = provider.generate_response("Test prompt")

        assert result == "This is a test response"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_generate_response_strips_whitespace(
        self, mock_post: MagicMock, provider: OllamaLlmProvider
    ) -> None:
        """Test that response strips whitespace."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "  Response with whitespace  "}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = provider.generate_response("Test prompt")

        assert result == "Response with whitespace"

    @patch("requests.post")
    def test_generate_response_connection_error(
        self, mock_post: MagicMock, provider: OllamaLlmProvider
    ) -> None:
        """Test handling of connection errors."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = provider.generate_response("Test prompt")

        assert "having trouble connecting" in result
        assert "Connection failed" in result

    @patch("requests.post")
    def test_chat_without_history(self, mock_post: MagicMock, provider: OllamaLlmProvider) -> None:
        """Test chat without conversation history."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Chat response"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = provider.chat("Hello", conversation_history=None)

        assert result == "Chat response"

    @patch("requests.post")
    def test_chat_with_history(self, mock_post: MagicMock, provider: OllamaLlmProvider) -> None:
        """Test chat with conversation history."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Response with context"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
        ]

        result = provider.chat("Second message", conversation_history=history)

        assert result == "Response with context"
        call_args = mock_post.call_args
        prompt = call_args[1]["json"]["prompt"]
        assert "User: First message" in prompt
        assert "Assistant: First response" in prompt
        assert "User: Second message" in prompt

    @patch("requests.get")
    def test_health_check_healthy(self, mock_get: MagicMock, provider: OllamaLlmProvider) -> None:
        """Test health check when service is healthy."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = provider.health_check()

        assert result["status"] == "healthy"
        assert result["provider"] == "ollama"
        assert result["model"] == "llama3.2"

    @patch("requests.get")
    def test_health_check_unhealthy(self, mock_get: MagicMock, provider: OllamaLlmProvider) -> None:
        """Test health check when service is unhealthy."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = provider.health_check()

        assert result["status"] == "unhealthy"
        assert result["provider"] == "ollama"

    @patch("requests.post")
    def test_chat_stream_success(self, mock_post: MagicMock, provider: OllamaLlmProvider) -> None:
        """Test successful streaming chat."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello "}',
            b'{"response": "world"}',
        ]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        chunks = list(provider.chat_stream("Test message"))

        assert len(chunks) == 2
        assert chunks[0] == "Hello "
        assert chunks[1] == "world"

    @patch("requests.post")
    def test_chat_stream_with_history(
        self, mock_post: MagicMock, provider: OllamaLlmProvider
    ) -> None:
        """Test streaming with conversation history."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"response": "Response"}']
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        history = [{"role": "user", "content": "Previous message"}]
        list(provider.chat_stream("Current message", conversation_history=history))

        call_args = mock_post.call_args
        prompt = call_args[1]["json"]["prompt"]
        assert "Previous message" in prompt

    @patch("requests.post")
    def test_chat_stream_connection_error(
        self, mock_post: MagicMock, provider: OllamaLlmProvider
    ) -> None:
        """Test streaming with connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        chunks = list(provider.chat_stream("Test message"))

        assert len(chunks) == 1
        assert "having trouble connecting" in chunks[0]


class TestOpenAiLlmProvider:
    """Tests for OpenAI LLM provider."""

    @pytest.fixture
    def provider(self) -> OpenAiLlmProvider:
        """Create OpenAI provider instance with mock client."""
        with patch("src.infrastructure.llm.openai_provider.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            provider = OpenAiLlmProvider(api_key="test-key", model_name="gpt-3.5-turbo")
            return provider

    @pytest.fixture
    def provider_no_key(self) -> OpenAiLlmProvider:
        """Create OpenAI provider without API key."""
        with patch("src.infrastructure.llm.openai_provider.OpenAI"):
            return OpenAiLlmProvider(api_key="", model_name="gpt-3.5-turbo")

    def test_initialization(self, provider: OpenAiLlmProvider) -> None:
        """Test provider initialization."""
        assert provider.api_key == "test-key"
        assert provider.model_name == "gpt-3.5-turbo"

    def test_initialization_no_key(self, provider_no_key: OpenAiLlmProvider) -> None:
        """Test provider initialization without API key."""
        assert provider_no_key.client is None

    def test_get_model_name(self, provider: OpenAiLlmProvider) -> None:
        """Test getting model name."""
        assert provider.get_model_name() == "gpt-3.5-turbo"

    def test_generate_response_no_client(self, provider_no_key: OpenAiLlmProvider) -> None:
        """Test generation without client."""
        result = provider_no_key.generate_response("Test")
        assert "API key not configured" in result

    def test_generate_response_success(self, provider: OpenAiLlmProvider) -> None:
        """Test successful response generation."""
        assert provider.client is not None
        assert isinstance(provider.client, MagicMock)

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.generate_response("Test prompt")

        assert result == "Test response"

    def test_generate_response_strips_whitespace(self, provider: OpenAiLlmProvider) -> None:
        """Test that response strips whitespace."""
        assert provider.client is not None
        assert isinstance(provider.client, MagicMock)

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="  Whitespace  "))]
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.generate_response("Test")

        assert result == "Whitespace"

    def test_generate_response_error(self, provider: OpenAiLlmProvider) -> None:
        """Test error handling."""
        provider.client.chat.completions.create.side_effect = Exception("API Error")

        result = provider.generate_response("Test")

        assert "Error connecting to OpenAI" in result

    def test_chat_without_history(self, provider: OpenAiLlmProvider) -> None:
        """Test chat without conversation history."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Chat response"))]
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.chat("Hello")

        assert result == "Chat response"

    def test_chat_with_history(self, provider: OpenAiLlmProvider) -> None:
        """Test chat with conversation history."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        provider.client.chat.completions.create.return_value = mock_response

        history = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response"},
        ]

        result = provider.chat("Second", conversation_history=history)

        assert result == "Response"
        call_args = provider.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 3

    def test_health_check_no_client(self, provider_no_key: OpenAiLlmProvider) -> None:
        """Test health check without client."""
        result = provider_no_key.health_check()

        assert result["status"] == "unhealthy"
        assert result["provider"] == "openai"

    def test_health_check_healthy(self, provider: OpenAiLlmProvider) -> None:
        """Test health check when service is healthy."""
        provider.client.models.list.return_value = []

        result = provider.health_check()

        assert result["status"] == "healthy"
        assert result["provider"] == "openai"

    def test_health_check_unhealthy(self, provider: OpenAiLlmProvider) -> None:
        """Test health check when service is unhealthy."""
        provider.client.models.list.side_effect = Exception("Connection error")

        result = provider.health_check()

        assert result["status"] == "unhealthy"

    def test_chat_stream_no_client(self, provider_no_key: OpenAiLlmProvider) -> None:
        """Test streaming without client."""
        chunks = list(provider_no_key.chat_stream("Test"))

        assert len(chunks) == 1
        assert "API key not configured" in chunks[0]

    def test_chat_stream_success(self, provider: OpenAiLlmProvider) -> None:
        """Test successful streaming."""
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock(delta=Mock(content="Hello "))]
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock(delta=Mock(content="world"))]

        provider.client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]

        chunks = list(provider.chat_stream("Test"))

        assert len(chunks) == 2
        assert chunks[0] == "Hello "
        assert chunks[1] == "world"


class TestClaudeLlmProvider:
    """Tests for Claude LLM provider."""

    @pytest.fixture
    def provider(self) -> ClaudeLlmProvider:
        """Create Claude provider instance with mock client."""
        with patch("src.infrastructure.llm.claude_provider.Anthropic"):
            provider = ClaudeLlmProvider(
                api_key="test-key", model_name="claude-3-5-sonnet-20241022"
            )
            provider.client = Mock()
            return provider

    @pytest.fixture
    def provider_no_key(self) -> ClaudeLlmProvider:
        """Create Claude provider without API key."""
        return ClaudeLlmProvider(api_key="", model_name="claude-3-5-sonnet-20241022")

    def test_initialization(self, provider: ClaudeLlmProvider) -> None:
        """Test provider initialization."""
        assert provider.api_key == "test-key"
        assert provider.model_name == "claude-3-5-sonnet-20241022"

    def test_get_model_name(self, provider: ClaudeLlmProvider) -> None:
        """Test getting model name."""
        assert provider.get_model_name() == "claude-3-5-sonnet-20241022"

    def test_generate_response_no_client(self, provider_no_key: ClaudeLlmProvider) -> None:
        """Test generation without client."""
        result = provider_no_key.generate_response("Test")
        assert "API key not configured" in result

    def test_generate_response_success(self, provider: ClaudeLlmProvider) -> None:
        """Test successful response generation."""
        mock_content = Mock()
        mock_content.text = "Test response"
        mock_response = Mock()
        mock_response.content = [mock_content]
        provider.client.messages.create.return_value = mock_response

        result = provider.generate_response("Test prompt")

        assert result == "Test response"

    def test_generate_response_strips_whitespace(self, provider: ClaudeLlmProvider) -> None:
        """Test that response strips whitespace."""
        mock_content = Mock()
        mock_content.text = "  Whitespace  "
        mock_response = Mock()
        mock_response.content = [mock_content]
        provider.client.messages.create.return_value = mock_response

        result = provider.generate_response("Test")

        assert result == "Whitespace"

    def test_generate_response_error(self, provider: ClaudeLlmProvider) -> None:
        """Test error handling."""
        provider.client.messages.create.side_effect = Exception("API Error")

        result = provider.generate_response("Test")

        assert "Error connecting to Claude" in result

    def test_chat_without_history(self, provider: ClaudeLlmProvider) -> None:
        """Test chat without conversation history."""
        mock_content = Mock()
        mock_content.text = "Chat response"
        mock_response = Mock()
        mock_response.content = [mock_content]
        provider.client.messages.create.return_value = mock_response

        result = provider.chat("Hello")

        assert result == "Chat response"

    def test_chat_with_history(self, provider: ClaudeLlmProvider) -> None:
        """Test chat with conversation history."""
        mock_content = Mock()
        mock_content.text = "Response"
        mock_response = Mock()
        mock_response.content = [mock_content]
        provider.client.messages.create.return_value = mock_response

        history = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response"},
        ]

        result = provider.chat("Second", conversation_history=history)

        assert result == "Response"
        call_args = provider.client.messages.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 3

    def test_health_check_no_client(self, provider_no_key: ClaudeLlmProvider) -> None:
        """Test health check without client."""
        result = provider_no_key.health_check()

        assert result["status"] == "unhealthy"
        assert result["provider"] == "claude"

    def test_health_check_healthy(self, provider: ClaudeLlmProvider) -> None:
        """Test health check when service is healthy."""
        mock_content = Mock()
        mock_content.text = "Hi"
        mock_response = Mock()
        mock_response.content = [mock_content]
        provider.client.messages.create.return_value = mock_response

        result = provider.health_check()

        assert result["status"] == "healthy"
        assert result["provider"] == "claude"

    def test_health_check_unhealthy(self, provider: ClaudeLlmProvider) -> None:
        """Test health check when service is unhealthy."""
        provider.client.messages.create.side_effect = Exception("Connection error")

        result = provider.health_check()

        assert result["status"] == "unhealthy"

    def test_chat_stream_no_client(self, provider_no_key: ClaudeLlmProvider) -> None:
        """Test streaming without client."""
        chunks = list(provider_no_key.chat_stream("Test"))

        assert len(chunks) == 1
        assert "API key not configured" in chunks[0]

    def test_chat_stream_success(self, provider: ClaudeLlmProvider) -> None:
        """Test successful streaming."""
        mock_stream = Mock()
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_stream.text_stream = iter(["Hello ", "world"])

        provider.client.messages.stream.return_value = mock_stream

        chunks = list(provider.chat_stream("Test"))

        assert len(chunks) == 2
        assert chunks[0] == "Hello "
        assert chunks[1] == "world"
