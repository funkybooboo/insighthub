"""Unit tests for LLM factory."""

from unittest.mock import MagicMock, patch

import pytest
from shared.llm.claude_provider import ClaudeLlmProvider
from shared.llm.factory import create_llm_provider, get_available_providers
from shared.llm.huggingface_provider import HuggingFaceLlmProvider
from shared.llm.ollama import OllamaLlmProvider
from shared.llm.openai_provider import OpenAiLlmProvider


class TestCreateLlmProvider:
    """Tests for create_llm_provider factory function."""

    @patch("shared.llm.factory.OllamaLlmProvider")
    def test_create_ollama_provider(self, mock_ollama: MagicMock) -> None:
        """Test creating Ollama provider."""
        provider = create_llm_provider("ollama")

        assert isinstance(provider, type(mock_ollama.return_value))

    @patch("shared.llm.factory.OllamaLlmProvider")
    def test_create_ollama_with_custom_params(self, mock_ollama: MagicMock) -> None:
        """Test creating Ollama with custom parameters."""
        create_llm_provider("ollama", base_url="http://custom:11434", model_name="custom-model")

        mock_ollama.assert_called_once_with(
            base_url="http://custom:11434", model_name="custom-model"
        )

    @patch("shared.llm.factory.OpenAiLlmProvider")
    def test_create_openai_provider(self, mock_openai: MagicMock) -> None:
        """Test creating OpenAI provider."""
        provider = create_llm_provider("openai")

        assert isinstance(provider, type(mock_openai.return_value))

    @patch("shared.llm.factory.OpenAiLlmProvider")
    def test_create_openai_with_custom_params(self, mock_openai: MagicMock) -> None:
        """Test creating OpenAI with custom parameters."""
        create_llm_provider("openai", api_key="custom-key", model_name="gpt-4")

        mock_openai.assert_called_once_with(api_key="custom-key", model_name="gpt-4")

    @patch("shared.llm.factory.ClaudeLlmProvider")
    def test_create_claude_provider(self, mock_claude: MagicMock) -> None:
        """Test creating Claude provider."""
        provider = create_llm_provider("claude")

        assert isinstance(provider, type(mock_claude.return_value))

    @patch("shared.llm.factory.ClaudeLlmProvider")
    def test_create_claude_with_custom_params(self, mock_claude: MagicMock) -> None:
        """Test creating Claude with custom parameters."""
        create_llm_provider("claude", api_key="custom-key", model_name="claude-3-opus")

        mock_claude.assert_called_once_with(api_key="custom-key", model_name="claude-3-opus")

    @patch("shared.llm.factory.HuggingFaceLlmProvider")
    def test_create_huggingface_provider(self, mock_hf: MagicMock) -> None:
        """Test creating HuggingFace provider."""
        provider = create_llm_provider("huggingface")

        assert isinstance(provider, type(mock_hf.return_value))

    @patch("shared.llm.factory.HuggingFaceLlmProvider")
    def test_create_huggingface_with_custom_params(self, mock_hf: MagicMock) -> None:
        """Test creating HuggingFace with custom parameters."""
        create_llm_provider(
            "huggingface",
            api_key="custom-key",
            model_name="custom-model",
            api_url="https://custom.url",
        )

        mock_hf.assert_called_once_with(
            api_key="custom-key", model_name="custom-model", api_url="https://custom.url"
        )

    def test_create_unknown_provider(self) -> None:
        """Test creating unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown LLM provider: unknown"):
            create_llm_provider("unknown")

    @patch("shared.llm.factory.LLM_PROVIDER", "openai")
    @patch("shared.llm.factory.OpenAiLlmProvider")
    def test_create_provider_uses_default(self, mock_openai: MagicMock) -> None:
        """Test that None provider uses default from config."""
        create_llm_provider(None)

        mock_openai.assert_called_once()


class TestGetAvailableProviders:
    """Tests for get_available_providers function."""

    @patch("shared.llm.factory.create_llm_provider")
    def test_get_available_providers_all_healthy(self, mock_create: MagicMock) -> None:
        """Test getting available providers when all are healthy."""
        mock_provider = type("MockProvider", (), {})()
        mock_provider.health_check = lambda: {
            "status": "healthy",
            "provider": "test",
        }
        mock_create.return_value = mock_provider

        result = get_available_providers()

        assert "ollama" in result
        assert "openai" in result
        assert "claude" in result
        assert "huggingface" in result

    @patch("shared.llm.factory.create_llm_provider")
    def test_get_available_providers_with_errors(self, mock_create: MagicMock) -> None:
        """Test getting available providers when health check raises errors."""

        def create_provider_side_effect(provider_name: str) -> object:
            mock_provider = type("MockProvider", (), {})()
            if provider_name == "ollama":
                mock_provider.health_check = lambda: {
                    "status": "healthy",
                    "provider": "ollama",
                }
            else:

                def raise_error() -> None:
                    raise Exception("Health check error")

                mock_provider.health_check = raise_error
            return mock_provider

        mock_create.side_effect = create_provider_side_effect

        result = get_available_providers()

        assert "ollama" in result
        assert result["openai"]["status"] == "error"
        assert result["claude"]["status"] == "error"
        assert result["huggingface"]["status"] == "error"


class TestProviderIntegration:
    """Integration tests for provider creation."""

    def test_create_all_providers_without_keys(self) -> None:
        """Test that all providers can be created without API keys."""
        with (
            patch("shared.llm.openai_provider.OpenAI"),
            patch("shared.llm.claude_provider.ANTHROPIC_AVAILABLE", True),
        ):
            ollama = create_llm_provider("ollama")
            openai = create_llm_provider("openai", api_key="")
            claude = create_llm_provider("claude", api_key="")
            huggingface = create_llm_provider("huggingface", api_key="")

            assert isinstance(ollama, OllamaLlmProvider)
            assert isinstance(openai, OpenAiLlmProvider)
            assert isinstance(claude, ClaudeLlmProvider)
            assert isinstance(huggingface, HuggingFaceLlmProvider)

    def test_provider_returns_correct_model_name(self) -> None:
        """Test that created providers return correct model names."""
        with (
            patch("shared.llm.openai_provider.OpenAI"),
            patch("shared.llm.claude_provider.ANTHROPIC_AVAILABLE", True),
        ):
            ollama = create_llm_provider("ollama", model_name="llama3.2")
            openai = create_llm_provider("openai", api_key="", model_name="gpt-4")
            claude = create_llm_provider(
                "claude", api_key="", model_name="claude-3-5-sonnet-20241022"
            )

            assert ollama.get_model_name() == "llama3.2"
            assert openai.get_model_name() == "gpt-4"
            assert claude.get_model_name() == "claude-3-5-sonnet-20241022"
