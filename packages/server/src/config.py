"""Centralized configuration module for reading environment variables."""

import os
from typing import Final

from dotenv import load_dotenv

# Load environment variables from the appropriate .env file
# Priority order:
# 1. .env.test (when running tests)
# 2. .env.local (local-only overrides, gitignored)
# 3. .env (standard development config, gitignored)
# 4. Environment variables (production)
if os.getenv("PYTEST_CURRENT_TEST"):
    # Running in pytest - use .env.test
    load_dotenv(".env.test", override=True)
else:
    # Load base .env first
    if os.path.exists(".env"):
        load_dotenv(".env")
    # Then load .env.local which overrides .env
    if os.path.exists(".env.local"):
        load_dotenv(".env.local", override=True)
# If no .env files exist, environment variables are expected to be set externally (production)

# Flask Configuration
FLASK_HOST: Final[str] = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT: Final[int] = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG: Final[bool] = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Database Configuration
DATABASE_URL: Final[str] = os.getenv(
    "DATABASE_URL", "postgresql://insighthub:insighthub_dev@localhost:5432/insighthub"
)
POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: Final[int] = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB", "insighthub")
POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER", "insighthub")
POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "insighthub")

# Repository Implementation Configuration
USER_REPOSITORY_TYPE: Final[str] = os.getenv("USER_REPOSITORY_TYPE", "sql")
DOCUMENT_REPOSITORY_TYPE: Final[str] = os.getenv("DOCUMENT_REPOSITORY_TYPE", "sql")
CHAT_SESSION_REPOSITORY_TYPE: Final[str] = os.getenv("CHAT_SESSION_REPOSITORY_TYPE", "sql")
CHAT_MESSAGE_REPOSITORY_TYPE: Final[str] = os.getenv("CHAT_MESSAGE_REPOSITORY_TYPE", "sql")

# Blob Storage Implementation Configuration
BLOB_STORAGE_TYPE: Final[str] = os.getenv("BLOB_STORAGE_TYPE", "file_system")

# File System Storage Configuration
FILE_SYSTEM_STORAGE_PATH: Final[str] = os.getenv("FILE_SYSTEM_STORAGE_PATH", "uploads")

# Blob Storage Configuration (MinIO/S3)
S3_ENDPOINT_URL: Final[str] = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_ACCESS_KEY: Final[str] = os.getenv("S3_ACCESS_KEY", "insighthub")
S3_SECRET_KEY: Final[str] = os.getenv("S3_SECRET_KEY", "insighthub_dev_secret")
S3_BUCKET_NAME: Final[str] = os.getenv("S3_BUCKET_NAME", "documents")

# Upload Configuration
UPLOAD_FOLDER: Final[str] = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_CONTENT_LENGTH: Final[int] = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))

# RAG Configuration
RAG_TYPE: Final[str] = os.getenv("RAG_TYPE", "vector")
CHUNKING_STRATEGY: Final[str] = os.getenv("CHUNKING_STRATEGY", "sentence")
CHUNK_SIZE: Final[int] = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP: Final[int] = int(os.getenv("CHUNK_OVERLAP", "50"))
RAG_TOP_K: Final[int] = int(os.getenv("RAG_TOP_K", "5"))

# Ollama Configuration
OLLAMA_BASE_URL: Final[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL: Final[str] = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
OLLAMA_EMBEDDING_MODEL: Final[str] = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Qdrant Configuration
QDRANT_HOST: Final[str] = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT: Final[int] = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME: Final[str] = os.getenv("QDRANT_COLLECTION_NAME", "insighthub")

# OpenAI Configuration
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: Final[str] = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Anthropic Configuration
ANTHROPIC_API_KEY: Final[str] = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: Final[str] = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# Hugging Face Configuration
HUGGINGFACE_API_KEY: Final[str] = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL: Final[str] = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

# LLM Provider Selection
LLM_PROVIDER: Final[str] = os.getenv("LLM_PROVIDER", "ollama")

# JWT Configuration
JWT_SECRET_KEY: Final[str] = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_EXPIRE_MINUTES: Final[int] = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# CORS Configuration
CORS_ORIGINS: Final[str] = os.getenv("CORS_ORIGINS", "*")

# Redis Configuration
REDIS_URL: Final[str] = os.getenv("REDIS_URL", "")

# Rate Limiting Configuration
RATE_LIMIT_ENABLED: Final[bool] = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE: Final[int] = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR: Final[int] = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

# Logging Configuration
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = os.getenv("LOG_FORMAT", "auto")  # "json", "console", or "auto"

# Performance Monitoring Configuration
SLOW_REQUEST_THRESHOLD: Final[float] = float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0"))
ENABLE_PERFORMANCE_STATS: Final[bool] = os.getenv("ENABLE_PERFORMANCE_STATS", "true").lower() == "true"


def validate_config() -> None:
    """
    Validate configuration values and raise errors for invalid configurations.

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate Flask configuration
    if not (1024 <= FLASK_PORT <= 65535):
        raise ValueError(f"FLASK_PORT must be between 1024 and 65535, got {FLASK_PORT}")

    # Validate database URL
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is required")

    # Validate JWT configuration
    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
        raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

    if not (60 <= JWT_EXPIRE_MINUTES <= 1440):  # 1 hour to 24 hours
        raise ValueError(f"JWT_EXPIRE_MINUTES must be between 60 and 1440, got {JWT_EXPIRE_MINUTES}")

    # Validate rate limiting
    if RATE_LIMIT_PER_MINUTE < 1 or RATE_LIMIT_PER_MINUTE > 1000:
        raise ValueError(f"RATE_LIMIT_PER_MINUTE must be between 1 and 1000, got {RATE_LIMIT_PER_MINUTE}")

    if RATE_LIMIT_PER_HOUR < 10 or RATE_LIMIT_PER_HOUR > 10000:
        raise ValueError(f"RATE_LIMIT_PER_HOUR must be between 10 and 10000, got {RATE_LIMIT_PER_HOUR}")

    # Validate Redis URL if provided
    if REDIS_URL and not REDIS_URL.startswith(("redis://", "rediss://", "unix://")):
        raise ValueError(f"REDIS_URL must start with redis://, rediss://, or unix://, got {REDIS_URL}")

    # Validate LLM provider
    valid_providers = ["ollama", "openai", "anthropic", "huggingface"]
    if LLM_PROVIDER not in valid_providers:
        raise ValueError(f"LLM_PROVIDER must be one of {valid_providers}, got {LLM_PROVIDER}")

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOG_LEVEL.upper() not in valid_log_levels:
        raise ValueError(f"LOG_LEVEL must be one of {valid_log_levels}, got {LOG_LEVEL}")

    print("Configuration validation passed")


# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    print(f"Configuration validation failed: {e}")
    raise

# RabbitMQ Configuration
RABBITMQ_HOST: Final[str] = os.getenv("RABBITMQ_HOST", "")
RABBITMQ_PORT: Final[int] = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER: Final[str] = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS: Final[str] = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_EXCHANGE: Final[str] = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
RABBITMQ_EXCHANGE_TYPE: Final[str] = os.getenv("RABBITMQ_EXCHANGE_TYPE", "topic")
