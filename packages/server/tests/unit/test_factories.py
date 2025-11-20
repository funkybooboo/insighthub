"""Unit tests for factory functions."""

from unittest.mock import Mock, patch

import pytest
from shared.llm.claude_provider import ClaudeLlmProvider
from shared.llm.factory import create_llm_provider
from shared.llm.huggingface_provider import HuggingFaceLlmProvider
from shared.llm.ollama import OllamaLlmProvider
from shared.llm.openai_provider import OpenAiLlmProvider
from shared.storage.file_system_blob_storage import FileSystemBlobStorage
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage
from shared.storage.minio_storage import MinIOBlobStorage

from src.infrastructure.storage.blob_storage_factory import BlobStorageType, create_blob_storage


class TestBlobStorageFactory:
    """Tests for blob storage factory."""

    @patch("src.infrastructure.storage.blob_storage_factory.config")
    def test_create_in_memory_storage(self, mock_config: Mock) -> None:
        """Test creating in-memory storage."""
        storage = create_blob_storage(BlobStorageType.IN_MEMORY)
        assert isinstance(storage, InMemoryBlobStorage)

    @patch("src.infrastructure.storage.blob_storage_factory.config")
    def test_create_file_system_storage(self, mock_config: Mock) -> None:
        """Test creating file system storage."""
        mock_config.FILE_SYSTEM_STORAGE_PATH = "/tmp/test"
        storage = create_blob_storage(BlobStorageType.FILE_SYSTEM)
        assert isinstance(storage, FileSystemBlobStorage)

    @patch("shared.storage.minio_storage.Minio")
    @patch("src.infrastructure.storage.blob_storage_factory.config")
    def test_create_s3_storage(self, mock_config: Mock, mock_minio: Mock) -> None:
        """Test creating S3 (MinIO) storage."""
        mock_config.S3_ENDPOINT_URL = "localhost:9000"
        mock_config.S3_ACCESS_KEY = "test_key"
        mock_config.S3_SECRET_KEY = "test_secret"
        mock_config.S3_BUCKET_NAME = "test_bucket"

        storage = create_blob_storage(BlobStorageType.S3)
        assert isinstance(storage, MinIOBlobStorage)

    @patch("src.infrastructure.storage.blob_storage_factory.config")
    def test_create_storage_from_config(self, mock_config: Mock) -> None:
        """Test creating storage from config when type is None."""
        mock_config.BLOB_STORAGE_TYPE = "in_memory"
        storage = create_blob_storage(None)
        assert isinstance(storage, InMemoryBlobStorage)

    def test_create_storage_invalid_type(self) -> None:
        """Test creating storage with invalid type."""
        with pytest.raises(ValueError, match="Unsupported blob storage type"):
            create_blob_storage("invalid_type")  # type: ignore[arg-type]

    def test_blob_storage_type_enum_values(self) -> None:
        """Test BlobStorageType enum values."""
        assert BlobStorageType.S3.value == "s3"
        assert BlobStorageType.FILE_SYSTEM.value == "file_system"
        assert BlobStorageType.IN_MEMORY.value == "in_memory"


class TestLlmProviderFactory:
    """Tests for LLM provider factory."""

    @patch("src.infrastructure.llm.factory.OLLAMA_BASE_URL", "http://localhost:11434")
    @patch("src.infrastructure.llm.factory.OLLAMA_LLM_MODEL", "llama3.2")
    def test_create_ollama_provider(self) -> None:
        """Test creating Ollama provider."""
        provider = create_llm_provider("ollama")
        assert isinstance(provider, OllamaLlmProvider)

    @patch("src.infrastructure.llm.factory.OPENAI_API_KEY", "test_key")
    @patch("src.infrastructure.llm.factory.OPENAI_MODEL", "gpt-3.5-turbo")
    def test_create_openai_provider(self) -> None:
        """Test creating OpenAI provider."""
        provider = create_llm_provider("openai")
        assert isinstance(provider, OpenAiLlmProvider)

    @patch("src.infrastructure.llm.factory.ANTHROPIC_API_KEY", "test_key")
    @patch("src.infrastructure.llm.factory.ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    def test_create_claude_provider(self) -> None:
        """Test creating Claude provider."""
        provider = create_llm_provider("claude")
        assert isinstance(provider, ClaudeLlmProvider)

    @patch("src.infrastructure.llm.factory.HUGGINGFACE_API_KEY", "test_key")
    @patch("src.infrastructure.llm.factory.HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
    def test_create_huggingface_provider(self) -> None:
        """Test creating HuggingFace provider."""
        provider = create_llm_provider("huggingface")
        assert isinstance(provider, HuggingFaceLlmProvider)

    @patch("src.infrastructure.llm.factory.LLM_PROVIDER", "ollama")
    @patch("src.infrastructure.llm.factory.OLLAMA_BASE_URL", "http://localhost:11434")
    @patch("src.infrastructure.llm.factory.OLLAMA_LLM_MODEL", "llama3.2")
    def test_create_provider_from_config(self) -> None:
        """Test creating provider from config when name is None."""
        provider = create_llm_provider(None)
        assert isinstance(provider, OllamaLlmProvider)

    def test_create_provider_invalid_name(self) -> None:
        """Test creating provider with invalid name."""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            create_llm_provider("invalid_provider")

    @patch("src.infrastructure.llm.factory.OLLAMA_BASE_URL", "http://localhost:11434")
    @patch("src.infrastructure.llm.factory.OLLAMA_LLM_MODEL", "llama3.2")
    def test_create_provider_with_kwargs(self) -> None:
        """Test creating provider with custom kwargs."""
        provider = create_llm_provider(
            "ollama", base_url="http://custom:11434", model_name="custom-model"
        )
        assert isinstance(provider, OllamaLlmProvider)
        assert provider.base_url == "http://custom:11434"
        assert provider.model_name == "custom-model"

    @patch("src.infrastructure.llm.factory.OPENAI_API_KEY", "default_key")
    @patch("src.infrastructure.llm.factory.OPENAI_MODEL", "gpt-3.5-turbo")
    def test_create_provider_kwargs_override_config(self) -> None:
        """Test that kwargs override config values."""
        provider = create_llm_provider("openai", api_key="custom_key", model_name="gpt-4")
        assert isinstance(provider, OpenAiLlmProvider)
        assert provider.api_key == "custom_key"
        assert provider.model_name == "gpt-4"

    @patch("src.infrastructure.llm.factory.ANTHROPIC_API_KEY", "default_key")
    @patch("src.infrastructure.llm.factory.ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    def test_create_claude_with_custom_key(self) -> None:
        """Test creating Claude provider with custom API key."""
        provider = create_llm_provider("claude", api_key="custom_claude_key")
        assert isinstance(provider, ClaudeLlmProvider)
        assert provider.api_key == "custom_claude_key"

    @patch("src.infrastructure.llm.factory.HUGGINGFACE_API_KEY", "default_key")
    @patch("src.infrastructure.llm.factory.HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
    def test_create_huggingface_with_custom_url(self) -> None:
        """Test creating HuggingFace provider with custom API URL."""
        provider = create_llm_provider("huggingface", api_url="https://custom.huggingface.co")
        assert isinstance(provider, HuggingFaceLlmProvider)

    def test_create_provider_error_message_lists_supported(self) -> None:
        """Test that error message lists supported providers."""
        with pytest.raises(ValueError) as exc_info:
            create_llm_provider("unsupported")

        error_message = str(exc_info.value)
        assert "ollama" in error_message
        assert "openai" in error_message
        assert "claude" in error_message
        assert "huggingface" in error_message


class TestGetAvailableProviders:
    """Tests for get_available_providers function."""

    @patch("src.infrastructure.llm.factory.create_llm_provider")
    def test_get_available_providers_calls_health_check(self, mock_create_provider: Mock) -> None:
        """Test that health checks are called for all providers."""
        from shared.llm.factory import get_available_providers

        mock_provider = type("MockProvider", (), {})()
        mock_provider.health_check = lambda: {"status": "healthy", "provider": "test"}
        mock_create_provider.return_value = mock_provider

        result = get_available_providers()

        assert "ollama" in result
        assert "openai" in result
        assert "claude" in result
        assert "huggingface" in result

    @patch("src.infrastructure.llm.factory.create_llm_provider")
    def test_get_available_providers_handles_errors(self, mock_create_provider: Mock) -> None:
        """Test that provider errors are handled gracefully."""
        from shared.llm.factory import get_available_providers

        mock_provider = type("MockProvider", (), {})()
        mock_provider.health_check = lambda: (_ for _ in ()).throw(Exception("Connection failed"))
        mock_create_provider.return_value = mock_provider

        result = get_available_providers()

        assert isinstance(result, dict)
        for _provider_name, status in result.items():
            assert "status" in status or "error" in status

    @patch("src.infrastructure.llm.factory.create_llm_provider")
    def test_get_available_providers_returns_dict(self, mock_create_provider: Mock) -> None:
        """Test that get_available_providers returns a dictionary."""
        from shared.llm.factory import get_available_providers

        mock_provider = type("MockProvider", (), {})()
        mock_provider.health_check = lambda: {"status": "healthy"}
        mock_create_provider.return_value = mock_provider

        result = get_available_providers()
        assert isinstance(result, dict)
        assert len(result) == 4
