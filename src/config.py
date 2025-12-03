"""Unified configuration system for server and workers."""

from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Environment(str):
    """Application environment enumeration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = Field(description="Database connection URL")


class RedisConfig(BaseModel):
    """Redis configuration."""

    url: Optional[str] = Field(default=None, description="Redis connection URL")
    default_ttl: int = Field(default=3600, description="Default cache TTL in seconds")


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="ollama", description="LLM provider to use")
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama API base URL"
    )
    ollama_llm_model: str = Field(default="llama3.2", description="Ollama LLM model name")
    ollama_embedding_model: str = Field(
        default="nomic-embed-text", description="Ollama embedding model name"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Anthropic model name"
    )
    huggingface_api_key: Optional[str] = Field(default=None, description="HuggingFace API key")
    huggingface_model: str = Field(
        default="meta-llama/Llama-3.2-3B-Instruct", description="HuggingFace model name"
    )


class SecurityConfig(BaseModel):
    """Security configuration."""

    secret_key: str = Field(description="Flask secret key", min_length=32)
    jwt_secret_key: str = Field(description="JWT secret key", min_length=32)
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=1440, description="JWT expiration in minutes")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], description="CORS allowed origins"
    )


class WorkerConfig(BaseModel):
    """Worker-specific configuration."""

    worker_name: str = Field(default="", description="Name of the worker")
    worker_concurrency: int = Field(default=2, description="Number of concurrent worker threads")
    chunk_size: int = Field(default=1000, description="Document chunk size")
    chunk_overlap: int = Field(default=200, description="Document chunk overlap")
    batch_size: int = Field(default=32, description="Batch processing size")


class StorageConfig(BaseModel):
    """Storage configuration."""

    blob_storage_type: str = Field(default="s3", description="Blob storage type")
    file_system_storage_path: str = Field(default="uploads", description="File system storage path")
    s3_endpoint_url: Optional[str] = Field(default=None, description="S3 endpoint URL")
    s3_access_key: Optional[str] = Field(default=None, description="S3 access key")
    s3_secret_key: Optional[str] = Field(default=None, description="S3 secret key")
    s3_bucket_name: str = Field(default="document", description="S3 bucket name")


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""

    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection_name: str = Field(default="insighthub", description="Qdrant collection name")


class GraphStoreConfig(BaseModel):
    """Graph store configuration."""

    neo4j_url: Optional[str] = Field(default=None, description="Neo4j connection URL")
    neo4j_user: Optional[str] = Field(default=None, description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")


class AppConfig(BaseSettings):
    """Unified configuration for server and workers."""

    # Environment
    environment: str = Field(default=Environment.DEVELOPMENT, description="Application environment")

    # Flask settings (server only)
    host: str = Field(default="0.0.0.0", description="Flask host")
    port: int = Field(default=5000, description="Flask port")
    debug: bool = Field(default=False, description="Flask debug mode")

    # Upload settings
    upload_folder: str = Field(default="uploads", description="Upload folder path")
    max_content_length: int = Field(default=16777216, description="Max upload size in bytes")

    # Database
    database_url: str = Field(
        default="postgresql://insighthub:insighthub_dev@localhost:5432/insighthub",
        description="Database connection URL",
    )

    # Redis
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_default_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_type: str = Field(default="in_memory", description="Cache type (in_memory or redis)")

    # LLM
    llm_provider: str = Field(default="ollama", description="LLM provider to use")
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama API base URL"
    )
    ollama_llm_model: str = Field(default="llama3.2", description="Ollama LLM model name")
    ollama_embedding_model: str = Field(
        default="nomic-embed-text", description="Ollama embedding model name"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Anthropic model name"
    )
    huggingface_api_key: Optional[str] = Field(default=None, description="HuggingFace API key")
    huggingface_model: str = Field(
        default="meta-llama/Llama-3.2-3B-Instruct", description="HuggingFace model name"
    )

    # Security (server only)
    secret_key: str = Field(
        default="dev-secret-key-32-chars-minimum-replace-in-prod",
        description="Flask secret key",
        min_length=32,
    )
    jwt_secret_key: str = Field(
        default="dev-jwt-secret-key-32-chars-minimum-replace-in-prod",
        description="JWT secret key",
        min_length=32,
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=1440, description="JWT expiration in minutes")
    cors_origins_str: str = Field(
        default="http://localhost:3000", description="CORS allowed origins (comma-separated)"
    )

    # Worker settings
    worker_name: str = Field(default="", description="Name of the worker")
    worker_concurrency: int = Field(default=2, description="Number of concurrent worker threads")

    # Processing settings
    chunk_size: int = Field(default=1000, description="Document chunk size")
    chunk_overlap: int = Field(default=200, description="Document chunk overlap")
    batch_size: int = Field(default=32, description="Batch processing size")

    # Storage (default: S3/MinIO for production)
    blob_storage_type: str = Field(default="s3", description="Blob storage type")
    file_system_storage_path: str = Field(default="uploads", description="File system storage path")
    s3_endpoint_url: Optional[str] = Field(
        default="http://localhost:9000", description="S3 endpoint URL (MinIO default)"
    )
    s3_access_key: Optional[str] = Field(default="minioadmin", description="S3 access key")
    s3_secret_key: Optional[str] = Field(default="minioadmin", description="S3 secret key")
    s3_bucket_name: str = Field(default="document", description="S3 bucket name")

    # Vector Store
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection_name: str = Field(default="insighthub", description="Qdrant collection name")

    # Graph Store
    neo4j_url: Optional[str] = Field(default=None, description="Neo4j connection URL")
    neo4j_user: Optional[str] = Field(default=None, description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")

    # Repository types
    user_repository_type: str = Field(default="memory", description="User repository type")
    workspace_repository_type: str = Field(
        default="memory", description="Workspace repository type"
    )
    document_repository_type: str = Field(default="memory", description="Document repository type")
    chat_session_repository_type: str = Field(
        default="memory", description="Chat session repository type"
    )
    chat_message_repository_type: str = Field(
        default="memory", description="Chat message repository type"
    )
    default_rag_config_repository_type: str = Field(
        default="memory", description="Default RAG config repository type"
    )

    # Legacy compatibility
    rate_limit_enabled: bool = Field(default=True, description="Rate limiting enabled")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="auto", description="Log format")
    slow_request_threshold: float = Field(default=1.0, description="Slow request threshold")
    enable_performance_stats: bool = Field(default=True, description="Enable performance stats")

    # Properties for backward compatibility and organization
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(url=self.database_url)

    @property
    def redis(self) -> RedisConfig:
        """Get Redis configuration."""
        return RedisConfig(url=self.redis_url, default_ttl=self.redis_default_ttl)

    @property
    def llm(self) -> LLMConfig:
        """Get LLM configuration."""
        return LLMConfig(
            provider=self.llm_provider,
            ollama_base_url=self.ollama_base_url,
            ollama_llm_model=self.ollama_llm_model,
            ollama_embedding_model=self.ollama_embedding_model,
            openai_api_key=self.openai_api_key,
            openai_model=self.openai_model,
            anthropic_api_key=self.anthropic_api_key,
            anthropic_model=self.anthropic_model,
            huggingface_api_key=self.huggingface_api_key,
            huggingface_model=self.huggingface_model,
        )

    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            secret_key=self.secret_key,
            jwt_secret_key=self.jwt_secret_key,
            jwt_algorithm=self.jwt_algorithm,
            jwt_expire_minutes=self.jwt_expire_minutes,
            cors_origins=[origin.strip() for origin in self.cors_origins_str.split(",")],
        )

    @property
    def worker(self) -> WorkerConfig:
        """Get worker configuration."""
        return WorkerConfig(
            worker_name=self.worker_name,
            worker_concurrency=self.worker_concurrency,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            batch_size=self.batch_size,
        )

    @property
    def storage(self) -> StorageConfig:
        """Get storage configuration."""
        return StorageConfig(
            blob_storage_type=self.blob_storage_type,
            file_system_storage_path=self.file_system_storage_path,
            s3_endpoint_url=self.s3_endpoint_url,
            s3_access_key=self.s3_access_key,
            s3_secret_key=self.s3_secret_key,
            s3_bucket_name=self.s3_bucket_name,
        )

    @property
    def vector_store(self) -> VectorStoreConfig:
        """Get vector store configuration."""
        return VectorStoreConfig(
            qdrant_host=self.qdrant_host,
            qdrant_port=self.qdrant_port,
            qdrant_collection_name=self.qdrant_collection_name,
        )

    @property
    def graph_store(self) -> GraphStoreConfig:
        """Get graph store configuration."""
        return GraphStoreConfig(
            neo4j_url=self.neo4j_url,
            neo4j_user=self.neo4j_user,
            neo4j_password=self.neo4j_password,
        )

    def validate_config(self) -> None:
        """Validate configuration and raise errors for invalid configurations."""
        errors: list[str] = []

        # Validate database URL
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        elif not self.database_url.startswith("postgresql://"):
            errors.append("DATABASE_URL must start with 'postgresql://'")

        # Validate blob storage configuration
        if self.blob_storage_type not in ["filesystem", "s3"]:
            errors.append(
                f"Invalid BLOB_STORAGE_TYPE: {self.blob_storage_type}. Must be 'filesystem' or 's3'"
            )

        if self.blob_storage_type == "s3":
            if not self.s3_endpoint_url:
                errors.append("S3_ENDPOINT_URL is required when using S3 storage")
            if not self.s3_access_key:
                errors.append("S3_ACCESS_KEY is required when using S3 storage")
            if not self.s3_secret_key:
                errors.append("S3_SECRET_KEY is required when using S3 storage")
            if not self.s3_bucket_name:
                errors.append("S3_BUCKET_NAME is required when using S3 storage")

        # Validate LLM provider configuration
        if self.llm_provider not in ["ollama", "openai", "claude", "huggingface"]:
            errors.append(
                f"Invalid LLM_PROVIDER: {self.llm_provider}. Must be 'ollama', 'openai', 'claude', or 'huggingface'"
            )

        if self.llm_provider == "ollama":
            if not self.ollama_base_url:
                errors.append("OLLAMA_BASE_URL is required when using Ollama")
            if not self.ollama_llm_model:
                errors.append("OLLAMA_LLM_MODEL is required when using Ollama")

        if self.llm_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when using OpenAI")

        if self.llm_provider == "claude" and not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required when using Claude")

        if self.llm_provider == "huggingface" and not self.huggingface_api_key:
            errors.append("HUGGINGFACE_API_KEY is required when using HuggingFace")

        # Validate numeric ranges
        if self.chunk_size <= 0:
            errors.append(f"CHUNK_SIZE must be positive, got {self.chunk_size}")

        if self.chunk_overlap < 0:
            errors.append(f"CHUNK_OVERLAP must be non-negative, got {self.chunk_overlap}")

        if self.chunk_overlap >= self.chunk_size:
            errors.append(
                f"CHUNK_OVERLAP ({self.chunk_overlap}) must be less than CHUNK_SIZE ({self.chunk_size})"
            )

        if self.batch_size <= 0:
            errors.append(f"BATCH_SIZE must be positive, got {self.batch_size}")

        # Validate security settings
        if len(self.secret_key) < 32:
            errors.append(f"SECRET_KEY must be at least 32 characters, got {len(self.secret_key)}")

        if len(self.jwt_secret_key) < 32:
            errors.append(
                f"JWT_SECRET_KEY must be at least 32 characters, got {len(self.jwt_secret_key)}"
            )

        # Raise all errors if any
        if errors:
            error_message = "Configuration validation failed:\n  - " + "\n  - ".join(errors)
            raise ValueError(error_message)


def load_config(env_file_path: Optional[str] = None) -> AppConfig:
    """Load configuration based on environment.

    Args:
        env_file_path: Optional path to .env file to load. If not provided,
                       automatically loads .env for development or .env.test for tests.
    """
    import os

    from dotenv import load_dotenv

    if env_file_path:
        # Load the specified .env file
        load_dotenv(env_file_path, override=True)
    else:
        # Auto-detect environment and load appropriate .env file
        if os.getenv("PYTEST_CURRENT_TEST"):
            # Running in pytest - load test configuration
            load_dotenv(".env.test", override=True)
        else:
            # Development/production - load main configuration
            load_dotenv(".env", override=True)

    # Create and validate config
    config = AppConfig()
    config.validate_config()

    return config


# Global config instance
config = load_config()
