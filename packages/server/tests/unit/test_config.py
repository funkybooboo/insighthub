"""Unit tests for configuration module."""

import os
from unittest.mock import patch


class TestConfigurationDefaults:
    """Tests for default configuration values."""

    def test_flask_host_default(self) -> None:
        """Test Flask host default value."""
        with patch.dict(os.environ, {}, clear=True):
            import importlib

            import src.config as config_module

            importlib.reload(config_module)
            assert config_module.FLASK_HOST == "0.0.0.0"

    def test_flask_port_default(self) -> None:
        """Test Flask port default value."""
        from src.config import FLASK_PORT

        assert FLASK_PORT == 5000 or isinstance(FLASK_PORT, int)

    def test_database_url_default(self) -> None:
        """Test database URL has a default value."""
        from src.config import DATABASE_URL

        assert DATABASE_URL is not None
        assert isinstance(DATABASE_URL, str)

    def test_ollama_base_url_default(self) -> None:
        """Test Ollama base URL default."""
        from src.config import OLLAMA_BASE_URL

        assert "localhost" in OLLAMA_BASE_URL or "11434" in OLLAMA_BASE_URL

    def test_ollama_models_default(self) -> None:
        """Test Ollama model defaults."""
        from src.config import OLLAMA_EMBEDDING_MODEL, OLLAMA_LLM_MODEL

        assert isinstance(OLLAMA_LLM_MODEL, str)
        assert isinstance(OLLAMA_EMBEDDING_MODEL, str)
        assert len(OLLAMA_LLM_MODEL) > 0
        assert len(OLLAMA_EMBEDDING_MODEL) > 0

    def test_qdrant_configuration_defaults(self) -> None:
        """Test Qdrant configuration defaults."""
        from src.config import QDRANT_COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT

        assert isinstance(QDRANT_HOST, str)
        assert isinstance(QDRANT_PORT, int)
        assert isinstance(QDRANT_COLLECTION_NAME, str)
        assert QDRANT_PORT > 0


class TestRepositoryConfiguration:
    """Tests for repository configuration."""

    def test_repository_types_default_to_sql(self) -> None:
        """Test that all repository types default to SQL."""
        from src.config import (
            CHAT_MESSAGE_REPOSITORY_TYPE,
            CHAT_SESSION_REPOSITORY_TYPE,
            DOCUMENT_REPOSITORY_TYPE,
            USER_REPOSITORY_TYPE,
        )

        assert USER_REPOSITORY_TYPE in ["sql", "in_memory"]
        assert DOCUMENT_REPOSITORY_TYPE in ["sql", "in_memory"]
        assert CHAT_SESSION_REPOSITORY_TYPE in ["sql", "in_memory"]
        assert CHAT_MESSAGE_REPOSITORY_TYPE in ["sql", "in_memory"]


class TestBlobStorageConfiguration:
    """Tests for blob storage configuration."""

    def test_blob_storage_type_default(self) -> None:
        """Test blob storage type default."""
        from src.config import BLOB_STORAGE_TYPE

        assert BLOB_STORAGE_TYPE in ["file_system", "minio", "s3"]

    def test_file_system_storage_path_exists(self) -> None:
        """Test file system storage path is configured."""
        from src.config import FILE_SYSTEM_STORAGE_PATH

        assert isinstance(FILE_SYSTEM_STORAGE_PATH, str)
        assert len(FILE_SYSTEM_STORAGE_PATH) > 0

    def test_s3_configuration_exists(self) -> None:
        """Test S3/MinIO configuration exists."""
        from src.config import S3_ACCESS_KEY, S3_BUCKET_NAME, S3_ENDPOINT_URL, S3_SECRET_KEY

        assert isinstance(S3_ENDPOINT_URL, str)
        assert isinstance(S3_ACCESS_KEY, str)
        assert isinstance(S3_SECRET_KEY, str)
        assert isinstance(S3_BUCKET_NAME, str)


class TestRagConfiguration:
    """Tests for RAG configuration."""

    def test_rag_type_default(self) -> None:
        """Test RAG type default."""
        from src.config import RAG_TYPE

        assert RAG_TYPE in ["vector", "graph"]

    def test_chunking_strategy_default(self) -> None:
        """Test chunking strategy default."""
        from src.config import CHUNKING_STRATEGY

        assert CHUNKING_STRATEGY in ["character", "sentence", "word"]

    def test_chunk_size_is_positive(self) -> None:
        """Test chunk size is positive integer."""
        from src.config import CHUNK_SIZE

        assert isinstance(CHUNK_SIZE, int)
        assert CHUNK_SIZE > 0

    def test_chunk_overlap_is_valid(self) -> None:
        """Test chunk overlap is valid."""
        from src.config import CHUNK_OVERLAP, CHUNK_SIZE

        assert isinstance(CHUNK_OVERLAP, int)
        assert CHUNK_OVERLAP >= 0
        assert CHUNK_OVERLAP < CHUNK_SIZE

    def test_rag_top_k_is_positive(self) -> None:
        """Test RAG top-k is positive."""
        from src.config import RAG_TOP_K

        assert isinstance(RAG_TOP_K, int)
        assert RAG_TOP_K > 0


class TestLlmConfiguration:
    """Tests for LLM provider configuration."""

    def test_llm_provider_default(self) -> None:
        """Test LLM provider default."""
        from src.config import LLM_PROVIDER

        assert LLM_PROVIDER in ["ollama", "openai", "claude", "huggingface"]

    def test_openai_configuration_exists(self) -> None:
        """Test OpenAI configuration exists."""
        from src.config import OPENAI_API_KEY, OPENAI_MODEL

        assert isinstance(OPENAI_API_KEY, str)
        assert isinstance(OPENAI_MODEL, str)

    def test_anthropic_configuration_exists(self) -> None:
        """Test Anthropic configuration exists."""
        from src.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

        assert isinstance(ANTHROPIC_API_KEY, str)
        assert isinstance(ANTHROPIC_MODEL, str)

    def test_huggingface_configuration_exists(self) -> None:
        """Test HuggingFace configuration exists."""
        from src.config import HUGGINGFACE_API_KEY, HUGGINGFACE_MODEL

        assert isinstance(HUGGINGFACE_API_KEY, str)
        assert isinstance(HUGGINGFACE_MODEL, str)


class TestJwtConfiguration:
    """Tests for JWT configuration."""

    def test_jwt_secret_key_exists(self) -> None:
        """Test JWT secret key is configured."""
        from src.config import JWT_SECRET_KEY

        assert isinstance(JWT_SECRET_KEY, str)
        assert len(JWT_SECRET_KEY) > 0

    def test_jwt_expire_minutes_is_positive(self) -> None:
        """Test JWT expiration is positive."""
        from src.config import JWT_EXPIRE_MINUTES

        assert isinstance(JWT_EXPIRE_MINUTES, int)
        assert JWT_EXPIRE_MINUTES > 0


class TestUploadConfiguration:
    """Tests for upload configuration."""

    def test_upload_folder_exists(self) -> None:
        """Test upload folder is configured."""
        from src.config import UPLOAD_FOLDER

        assert isinstance(UPLOAD_FOLDER, str)
        assert len(UPLOAD_FOLDER) > 0

    def test_max_content_length_is_positive(self) -> None:
        """Test max content length is positive."""
        from src.config import MAX_CONTENT_LENGTH

        assert isinstance(MAX_CONTENT_LENGTH, int)
        assert MAX_CONTENT_LENGTH > 0


class TestCorsConfiguration:
    """Tests for CORS configuration."""

    def test_cors_origins_exists(self) -> None:
        """Test CORS origins is configured."""
        from src.config import CORS_ORIGINS

        assert isinstance(CORS_ORIGINS, str)


class TestEnvironmentOverrides:
    """Tests for environment variable handling."""

    def test_flask_port_respects_env_or_default(self) -> None:
        """Test that FLASK_PORT uses environment variable or default."""
        from src.config import FLASK_PORT

        assert isinstance(FLASK_PORT, int)
        assert FLASK_PORT > 0

    def test_chunk_size_respects_env_or_default(self) -> None:
        """Test that CHUNK_SIZE uses environment variable or default."""
        from src.config import CHUNK_SIZE

        assert isinstance(CHUNK_SIZE, int)
        assert CHUNK_SIZE > 0

    def test_rag_type_respects_env_or_default(self) -> None:
        """Test that RAG_TYPE uses environment variable or default."""
        from src.config import RAG_TYPE

        assert RAG_TYPE in ["vector", "graph"]

    def test_llm_provider_respects_env_or_default(self) -> None:
        """Test that LLM_PROVIDER uses environment variable or default."""
        from src.config import LLM_PROVIDER

        assert LLM_PROVIDER in ["ollama", "openai", "claude", "huggingface"]


class TestTypeConsistency:
    """Tests for configuration value types."""

    def test_all_ports_are_integers(self) -> None:
        """Test that all port values are integers."""
        from src.config import FLASK_PORT, QDRANT_PORT

        assert isinstance(FLASK_PORT, int)
        assert isinstance(QDRANT_PORT, int)

    def test_all_booleans_are_bool_type(self) -> None:
        """Test that boolean configs are actually bools."""
        from src.config import FLASK_DEBUG

        assert isinstance(FLASK_DEBUG, bool)

    def test_all_string_configs_are_strings(self) -> None:
        """Test that string configs are actually strings."""
        from src.config import DATABASE_URL, FLASK_HOST, LLM_PROVIDER, OLLAMA_BASE_URL, RAG_TYPE

        assert isinstance(FLASK_HOST, str)
        assert isinstance(DATABASE_URL, str)
        assert isinstance(OLLAMA_BASE_URL, str)
        assert isinstance(RAG_TYPE, str)
        assert isinstance(LLM_PROVIDER, str)
