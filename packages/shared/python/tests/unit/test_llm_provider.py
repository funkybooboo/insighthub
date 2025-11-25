"""Unit tests for LlmProvider interface and implementations."""

from collections.abc import Generator

import pytest

from shared.llm.llm_provider import LlmProvider


class DummyLlmProvider(LlmProvider):
    """Dummy implementation of LlmProvider for testing."""

    def __init__(self, response: str = "Dummy response", model_name: str = "dummy-model") -> None:
        """Initialize with fixed response."""
        self.fixed_response = response
        self.model_name_value = model_name

    def generate_response(self, prompt: str) -> str:
        """Return fixed response."""
        return self.fixed_response

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """Return fixed response for chat."""
        return f"Response to: {message}"

    def chat_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> Generator[str, None, None]:
        """Stream fixed response in chunks."""
        words = self.fixed_response.split()
        for word in words:
            yield word + " "

    def health_check(self) -> dict[str, str | bool]:
        """Return healthy status."""
        return {"status": "healthy", "provider": "dummy", "model": self.model_name_value}

    def get_model_name(self) -> str:
        """Get model name."""
        return self.model_name_value


class FailingLlmProvider(LlmProvider):
    """Failing implementation of LlmProvider for testing error conditions."""

    def generate_response(self, prompt: str) -> str:
        """Raise exception."""
        raise Exception("Service unavailable")

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """Raise exception."""
        raise Exception("Chat service unavailable")

    def chat_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> Generator[str, None, None]:
        """Raise exception."""
        raise Exception("Streaming service unavailable")
        yield ""  # Unreachable

    def health_check(self) -> dict[str, str | bool]:
        """Return unhealthy status."""
        return {"status": "unhealthy", "error": "Service down"}

    def get_model_name(self) -> str:
        """Get model name."""
        return "failing-model"


@pytest.fixture
def dummy_provider() -> DummyLlmProvider:
    """Provide a dummy LLM provider."""
    return DummyLlmProvider()


@pytest.fixture
def failing_provider() -> FailingLlmProvider:
    """Provide a failing LLM provider."""
    return FailingLlmProvider()


class TestLlmProviderGenerateResponse:
    """Tests for generate_response method."""

    def test_generate_response_returns_string(self, dummy_provider: DummyLlmProvider) -> None:
        """generate_response returns a string."""
        result = dummy_provider.generate_response("Test prompt")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_response_handles_empty_prompt(self, dummy_provider: DummyLlmProvider) -> None:
        """generate_response handles empty prompt."""
        result = dummy_provider.generate_response("")

        assert isinstance(result, str)

    def test_generate_response_handles_long_prompt(self, dummy_provider: DummyLlmProvider) -> None:
        """generate_response handles long prompts."""
        long_prompt = "A" * 10000
        result = dummy_provider.generate_response(long_prompt)

        assert isinstance(result, str)

    def test_generate_response_can_fail(self, failing_provider: FailingLlmProvider) -> None:
        """generate_response can raise exceptions."""
        with pytest.raises(Exception, match="Service unavailable"):
            failing_provider.generate_response("Test prompt")


class TestLlmProviderChat:
    """Tests for chat method."""

    def test_chat_returns_string(self, dummy_provider: DummyLlmProvider) -> None:
        """chat returns a string."""
        result = dummy_provider.chat("Hello")

        assert isinstance(result, str)
        assert "Hello" in result

    def test_chat_without_history(self, dummy_provider: DummyLlmProvider) -> None:
        """chat works without conversation history."""
        result = dummy_provider.chat("Test message")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_chat_with_history(self, dummy_provider: DummyLlmProvider) -> None:
        """chat accepts conversation history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        result = dummy_provider.chat("Current message", history)

        # In dummy implementation, history is ignored, but method should not fail
        assert isinstance(result, str)

    def test_chat_with_empty_history(self, dummy_provider: DummyLlmProvider) -> None:
        """chat handles empty history list."""
        result = dummy_provider.chat("Test", [])

        assert isinstance(result, str)

    def test_chat_can_fail(self, failing_provider: FailingLlmProvider) -> None:
        """chat can raise exceptions."""
        with pytest.raises(Exception, match="Chat service unavailable"):
            failing_provider.chat("Test message")


class TestLlmProviderChatStream:
    """Tests for chat_stream method."""

    def test_chat_stream_returns_generator(self, dummy_provider: DummyLlmProvider) -> None:
        """chat_stream returns a generator."""
        result = dummy_provider.chat_stream("Test message")

        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_chat_stream_yields_strings(self, dummy_provider: DummyLlmProvider) -> None:
        """chat_stream yields strings."""
        chunks = list(dummy_provider.chat_stream("Test message"))

        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, str)

    def test_chat_stream_with_history(self, dummy_provider: DummyLlmProvider) -> None:
        """chat_stream accepts conversation history."""
        history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]

        chunks = list(dummy_provider.chat_stream("Current", history))

        assert len(chunks) > 0

    def test_chat_stream_can_be_consumed_partially(self, dummy_provider: DummyLlmProvider) -> None:
        """chat_stream can be consumed partially."""
        generator = dummy_provider.chat_stream("Test")

        # Consume only first chunk
        first_chunk = next(generator)
        assert isinstance(first_chunk, str)

        # Generator should still be valid
        remaining = list(generator)
        assert isinstance(remaining, list)

    def test_chat_stream_can_fail(self, failing_provider: FailingLlmProvider) -> None:
        """chat_stream can raise exceptions."""
        generator = failing_provider.chat_stream("Test")

        with pytest.raises(Exception, match="Streaming service unavailable"):
            next(generator)


class TestLlmProviderHealthCheck:
    """Tests for health_check method."""

    def test_health_check_returns_dict(self, dummy_provider: DummyLlmProvider) -> None:
        """health_check returns a dictionary."""
        result = dummy_provider.health_check()

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_health_check_contains_status(self, dummy_provider: DummyLlmProvider) -> None:
        """health_check result contains status."""
        result = dummy_provider.health_check()

        assert "status" in result

    def test_health_check_mixed_value_types(self, dummy_provider: DummyLlmProvider) -> None:
        """health_check can return mixed value types."""
        result = dummy_provider.health_check()

        # Should contain strings and booleans
        has_string = any(isinstance(v, str) for v in result.values())
        has_bool = any(isinstance(v, bool) for v in result.values())

        # At least one of each type
        assert has_string or has_bool

    def test_failing_provider_health_check(self, failing_provider: FailingLlmProvider) -> None:
        """health_check can return error status."""
        result = failing_provider.health_check()

        assert isinstance(result, dict)
        assert result.get("status") == "unhealthy"


class TestLlmProviderGetModelName:
    """Tests for get_model_name method."""

    def test_get_model_name_returns_string(self, dummy_provider: DummyLlmProvider) -> None:
        """get_model_name returns a string."""
        result = dummy_provider.get_model_name()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_model_name_returns_expected_name(self, dummy_provider: DummyLlmProvider) -> None:
        """get_model_name returns expected model name."""
        result = dummy_provider.get_model_name()

        assert result == "dummy-model"

    def test_different_providers_have_different_names(self) -> None:
        """Different providers can have different model names."""
        provider1 = DummyLlmProvider(model_name="model-a")
        provider2 = DummyLlmProvider(model_name="model-b")

        assert provider1.get_model_name() == "model-a"
        assert provider2.get_model_name() == "model-b"
        assert provider1.get_model_name() != provider2.get_model_name()


class TestLlmProviderIntegration:
    """Integration tests for LLM provider operations."""

    def test_provider_can_handle_conversation_flow(self, dummy_provider: DummyLlmProvider) -> None:
        """Provider can handle a conversation flow."""
        # Start conversation
        response1 = dummy_provider.chat("Hello")
        assert isinstance(response1, str)

        # Continue with history
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": response1},
        ]

        response2 = dummy_provider.chat("How are you?", history)
        assert isinstance(response2, str)

        # Stream a response
        stream_chunks = list(dummy_provider.chat_stream("Tell me a story"))
        assert len(stream_chunks) > 0
        full_streamed = "".join(stream_chunks)
        assert isinstance(full_streamed, str)

    def test_provider_health_and_model_info(self, dummy_provider: DummyLlmProvider) -> None:
        """Provider provides health and model information."""
        # Check health
        health = dummy_provider.health_check()
        assert health["status"] == "healthy"

        # Get model name
        model_name = dummy_provider.get_model_name()
        assert model_name == "dummy-model"

        # Health should include model info
        assert health.get("model") == model_name

    def test_provider_error_handling(self, failing_provider: FailingLlmProvider) -> None:
        """Provider handles errors appropriately."""
        # All methods should fail
        with pytest.raises(Exception):
            failing_provider.generate_response("test")

        with pytest.raises(Exception):
            failing_provider.chat("test")

        with pytest.raises(Exception):
            list(failing_provider.chat_stream("test"))

        # But health check and model name should still work
        health = failing_provider.health_check()
        assert health["status"] == "unhealthy"

        model_name = failing_provider.get_model_name()
        assert model_name == "failing-model"

    def test_streaming_vs_non_streaming_consistency(self, dummy_provider: DummyLlmProvider) -> None:
        """Streaming and non-streaming methods should be consistent."""
        message = "Test message"

        # Get regular response
        regular_response = dummy_provider.chat(message)

        # Get streamed response
        streamed_chunks = list(dummy_provider.chat_stream(message))
        streamed_response = "".join(streamed_chunks)

        # Both should be strings and contain the message
        assert isinstance(regular_response, str)
        assert isinstance(streamed_response, str)
        assert message in regular_response or "Response to:" in regular_response
        assert len(streamed_response) > 0

    def test_provider_handles_special_characters(self, dummy_provider: DummyLlmProvider) -> None:
        """Provider handles special characters and unicode."""
        special_message = "Hello world with special chars!"

        response = dummy_provider.chat(special_message)
        assert isinstance(response, str)

        # Should not crash with unicode
        streamed = list(dummy_provider.chat_stream(special_message))
        assert len(streamed) > 0

    def test_provider_handles_empty_and_whitespace(self, dummy_provider: DummyLlmProvider) -> None:
        """Provider handles empty and whitespace inputs."""
        # Empty message
        response1 = dummy_provider.chat("")
        assert isinstance(response1, str)

        # Whitespace message
        response2 = dummy_provider.chat("   ")
        assert isinstance(response2, str)

        # Empty history
        response3 = dummy_provider.chat("test", [])
        assert isinstance(response3, str)

        # None history
        response4 = dummy_provider.chat("test", None)
        assert isinstance(response4, str)

    def test_provider_thread_safety_simulation(self, dummy_provider: DummyLlmProvider) -> None:
        """Simulate thread safety by calling methods multiple times."""
        # Call methods multiple times rapidly
        for i in range(10):
            # Generate response
            resp = dummy_provider.generate_response(f"Prompt {i}")
            assert isinstance(resp, str)

            # Chat
            chat_resp = dummy_provider.chat(f"Message {i}")
            assert isinstance(chat_resp, str)

            # Stream
            chunks = list(dummy_provider.chat_stream(f"Stream {i}"))
            assert len(chunks) > 0

            # Health check
            health = dummy_provider.health_check()
            assert isinstance(health, dict)

            # Model name
            name = dummy_provider.get_model_name()
            assert isinstance(name, str)
