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
