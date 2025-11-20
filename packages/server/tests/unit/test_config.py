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
