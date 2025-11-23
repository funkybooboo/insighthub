"""
Behavior tests for LLM provider factory.

These tests verify WHAT the factory does (inputs/outputs),
not HOW it does it (implementation details).
"""

import pytest

from shared.llm import (
    SUPPORTED_LLM_PROVIDERS,
    ClaudeLlmProvider,
    HuggingFaceLlmProvider,
    OllamaLlmProvider,
    OpenAiLlmProvider,
    create_llm_provider,
)


class TestLlmProviderFactoryBehavior:
    """Test LLM provider factory input/output behavior."""

    def test_create_ollama_returns_ollama_provider(self) -> None:
        """Given 'ollama' and config, returns OllamaLlmProvider."""
        provider = create_llm_provider(
            "ollama",
            base_url="http://localhost:11434",
            model_name="llama3.2",
        )

        assert isinstance(provider, OllamaLlmProvider)
        assert provider.base_url == "http://localhost:11434"
        assert provider.model_name == "llama3.2"

    def test_create_openai_returns_openai_provider(self) -> None:
        """Given 'openai' and config, returns OpenAiLlmProvider."""
        provider = create_llm_provider(
            "openai",
            api_key="sk-test-key",
            model_name="gpt-4",
        )

        assert isinstance(provider, OpenAiLlmProvider)
        assert provider.api_key == "sk-test-key"
        assert provider.model_name == "gpt-4"

    def test_create_claude_returns_claude_provider(self) -> None:
        """Given 'claude' and config, returns ClaudeLlmProvider."""
        provider = create_llm_provider(
            "claude",
            api_key="sk-ant-test",
            model_name="claude-3-5-sonnet-20241022",
        )

        assert isinstance(provider, ClaudeLlmProvider)
        assert provider.api_key == "sk-ant-test"
        assert provider.model_name == "claude-3-5-sonnet-20241022"

    def test_create_huggingface_returns_huggingface_provider(self) -> None:
        """Given 'huggingface' and config, returns HuggingFaceLlmProvider."""
        provider = create_llm_provider(
            "huggingface",
            api_key="hf-test-key",
            model_name="meta-llama/Llama-3.2-3B-Instruct",
        )

        assert isinstance(provider, HuggingFaceLlmProvider)

    def test_create_unknown_provider_raises(self) -> None:
        """Given unknown provider type, raises ValueError."""
        with pytest.raises(ValueError, match="Unknown LLM provider type"):
            create_llm_provider("unknown_type")

    def test_error_message_lists_supported_providers(self) -> None:
        """Error message for unknown provider lists valid options."""
        with pytest.raises(ValueError) as exc_info:
            create_llm_provider("invalid")

        error_msg = str(exc_info.value)
        for provider_type in SUPPORTED_LLM_PROVIDERS:
            assert provider_type in error_msg

    def test_ollama_requires_base_url(self) -> None:
        """Ollama requires base_url parameter."""
        with pytest.raises(ValueError, match="base_url"):
            create_llm_provider("ollama", model_name="llama3.2")

    def test_ollama_requires_model_name(self) -> None:
        """Ollama requires model_name parameter."""
        with pytest.raises(ValueError, match="model_name"):
            create_llm_provider("ollama", base_url="http://localhost:11434")

    def test_openai_requires_api_key(self) -> None:
        """OpenAI requires api_key parameter."""
        with pytest.raises(ValueError, match="api_key"):
            create_llm_provider("openai", model_name="gpt-4")

    def test_openai_requires_model_name(self) -> None:
        """OpenAI requires model_name parameter."""
        with pytest.raises(ValueError, match="model_name"):
            create_llm_provider("openai", api_key="sk-test")

    def test_claude_requires_api_key(self) -> None:
        """Claude requires api_key parameter."""
        with pytest.raises(ValueError, match="api_key"):
            create_llm_provider("claude", model_name="claude-3-5-sonnet")

    def test_huggingface_requires_api_key(self) -> None:
        """HuggingFace requires api_key parameter."""
        with pytest.raises(ValueError, match="api_key"):
            create_llm_provider("huggingface", model_name="llama")


class TestSupportedLlmProvidersList:
    """Test SUPPORTED_LLM_PROVIDERS constant."""

    def test_contains_all_expected_providers(self) -> None:
        """SUPPORTED_LLM_PROVIDERS contains all expected provider types."""
        assert "ollama" in SUPPORTED_LLM_PROVIDERS
        assert "openai" in SUPPORTED_LLM_PROVIDERS
        assert "claude" in SUPPORTED_LLM_PROVIDERS
        assert "huggingface" in SUPPORTED_LLM_PROVIDERS

    def test_is_list_of_strings(self) -> None:
        """SUPPORTED_LLM_PROVIDERS is a list of strings."""
        assert isinstance(SUPPORTED_LLM_PROVIDERS, list)
        for provider_type in SUPPORTED_LLM_PROVIDERS:
            assert isinstance(provider_type, str)
