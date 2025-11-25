# Configuration constants for backward compatibility
import os

FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
REDIS_URL = os.environ.get("REDIS_URL", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_LLM_MODEL = os.environ.get("OLLAMA_LLM_MODEL", "llama3.2")
QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "insighthub")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "test-jwt-secret-key-32-chars-minimum")
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "1440"))
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
LOG_FORMAT = os.environ.get("LOG_FORMAT", "json")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
BLOB_STORAGE_TYPE = os.environ.get("BLOB_STORAGE_TYPE", "file_system")
FILE_SYSTEM_STORAGE_PATH = os.environ.get("FILE_SYSTEM_STORAGE_PATH", "uploads")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "test-access-key")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "documents")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "test-secret-key")
CHAT_MESSAGE_REPOSITORY_TYPE = os.environ.get("CHAT_MESSAGE_REPOSITORY_TYPE", "sql")
CHAT_SESSION_REPOSITORY_TYPE = os.environ.get("CHAT_SESSION_REPOSITORY_TYPE", "sql")
DOCUMENT_REPOSITORY_TYPE = os.environ.get("DOCUMENT_REPOSITORY_TYPE", "sql")
USER_REPOSITORY_TYPE = os.environ.get("USER_REPOSITORY_TYPE", "sql")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.environ.get("HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE", "insighthub")
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", "16777216"))
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", "1000"))
SLOW_REQUEST_THRESHOLD = float(os.environ.get("SLOW_REQUEST_THRESHOLD", "1.0"))
ENABLE_PERFORMANCE_STATS = os.environ.get("ENABLE_PERFORMANCE_STATS", "True").lower() == "true"


def validate_config() -> None:
    """Validate configuration values and raise ValueError for invalid settings."""
    # Validate FLASK_PORT
    if not (1024 <= FLASK_PORT <= 65535):
        raise ValueError("FLASK_PORT must be between 1024 and 65535")

    # Validate DATABASE_URL
    if not DATABASE_URL or not DATABASE_URL.strip():
        raise ValueError("DATABASE_URL is required")

    # Validate JWT_SECRET_KEY
    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
        raise ValueError("JWT_SECRET_KEY must be at least 32 characters")

    # Validate JWT_EXPIRE_MINUTES
    if not (60 <= JWT_EXPIRE_MINUTES <= 1440):
        raise ValueError("JWT_EXPIRE_MINUTES must be between 60 and 1440")

    # Validate RATE_LIMIT_PER_MINUTE
    if not (1 <= RATE_LIMIT_PER_MINUTE <= 1000):
        raise ValueError("RATE_LIMIT_PER_MINUTE must be between 1 and 1000")

    # Validate RATE_LIMIT_PER_HOUR
    if not (10 <= RATE_LIMIT_PER_HOUR <= 10000):
        raise ValueError("RATE_LIMIT_PER_HOUR must be between 10 and 10000")

    # Validate REDIS_URL
    if REDIS_URL and not (
        REDIS_URL.startswith("redis://")
        or REDIS_URL.startswith("rediss://")
        or REDIS_URL.startswith("unix://")
    ):
        raise ValueError("REDIS_URL must start with redis://, rediss://, or unix://")

    # Validate LLM_PROVIDER
    valid_llm_providers = ["ollama", "openai", "anthropic", "huggingface"]
    if LLM_PROVIDER not in valid_llm_providers:
        raise ValueError(f"LLM_PROVIDER must be one of: {', '.join(valid_llm_providers)}")

    # Validate LOG_LEVEL
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOG_LEVEL.upper() not in valid_log_levels:
        raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")


class MockConfig:
    """Mock config class for testing with proper type annotations."""

    def __init__(self) -> None:
        self.host = "0.0.0.0"
        self.port = 5000
        self.debug = False
        self.database_url = "postgresql://test:test@localhost:5432/test"
        self.redis_url = None
        self.jwt_secret_key = "test-jwt-secret-key-32-chars-minimum"
        self.jwt_expire_minutes = 1440
        self.cors_origins = ["http://localhost:3000"]
        self.upload_folder = "uploads"
        self.max_content_length = 16777216
        self.rate_limit_enabled = True
        self.rate_limit_per_minute = 60
        self.rate_limit_per_hour = 1000
        self.log_level = "INFO"
        self.log_format = "json"
        self.slow_request_threshold = 1.0
        self.enable_performance_stats = True
        self.blob_storage_type = "filesystem"
        self.file_system_storage_path = "uploads"
        self.s3_endpoint_url = None
        self.s3_access_key = None
        self.s3_secret_key = None
        self.s3_bucket_name = "documents"
        self.llm_provider = "ollama"
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_llm_model = "llama3.2"
        self.ollama_embedding_model = "nomic-embed-text"
        self.openai_api_key = None
        self.openai_model = "gpt-3.5-turbo"
        self.anthropic_api_key = None
        self.anthropic_model = "claude-3-5-sonnet-20241022"
        self.huggingface_api_key = None
        self.huggingface_model = "meta-llama/Llama-3.2-3B-Instruct"
        self.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
        self.rabbitmq_exchange = "insighthub"
        self.qdrant_host = "localhost"
        self.qdrant_port = 6333
        self.qdrant_collection_name = "insighthub"
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.batch_size = 32

    # Properties for compatibility
    @property
    def database(self) -> object:
        class DB:
            def __init__(self, url: str) -> None:
                self.url = url

        return DB(self.database_url)

    @property
    def redis(self) -> object:
        class Redis:
            def __init__(self, url: str | None) -> None:
                self.url = url
                self.default_ttl = 3600

        return Redis(self.redis_url)

    @property
    def security(self) -> object:
        class Security:
            def __init__(
                self, jwt_secret_key: str, jwt_expire_minutes: int, cors_origins: list[str]
            ) -> None:
                self.jwt_secret_key = jwt_secret_key
                self.jwt_expire_minutes = jwt_expire_minutes
                self.cors_origins = cors_origins

        return Security(self.jwt_secret_key, self.jwt_expire_minutes, self.cors_origins)

    @property
    def storage(self) -> object:
        class Storage:
            def __init__(
                self,
                blob_storage_type: str,
                file_system_storage_path: str,
                s3_endpoint_url: str | None,
                s3_access_key: str | None,
                s3_secret_key: str | None,
                s3_bucket_name: str,
            ) -> None:
                self.blob_storage_type = blob_storage_type
                self.file_system_storage_path = file_system_storage_path
                self.s3_endpoint_url = s3_endpoint_url
                self.s3_access_key = s3_access_key
                self.s3_secret_key = s3_secret_key
                self.s3_bucket_name = s3_bucket_name

        return Storage(
            self.blob_storage_type,
            self.file_system_storage_path,
            self.s3_endpoint_url,
            self.s3_access_key,
            self.s3_secret_key,
            self.s3_bucket_name,
        )

    @property
    def vector_store(self) -> object:
        class VectorStore:
            def __init__(
                self, qdrant_host: str, qdrant_port: int, qdrant_collection_name: str
            ) -> None:
                self.qdrant_host = qdrant_host
                self.qdrant_port = qdrant_port
                self.qdrant_collection_name = qdrant_collection_name

        return VectorStore(self.qdrant_host, self.qdrant_port, self.qdrant_collection_name)


# Create mock config instance
config = MockConfig()
