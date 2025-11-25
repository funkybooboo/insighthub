"""
InsightHub Shared Library.

This package contains shared types, interfaces, events, and utilities
used across the InsightHub server and worker processes.

Modules:
    types: Core data types (Document, Chunk, GraphNode, Result, Option)
    rag: RAG interfaces, implementations, and orchestrators
    events: Event schemas for RabbitMQ messaging
    messaging: RabbitMQ publisher and consumer utilities
    blob_storage: Blob storage interface and implementations
    llm: LLM provider interfaces and implementations
    models: Data models (plain dataclasses)
    repositories: Data access layer
    database: Database connection utilities (SqlDatabase interface)
    logging: Structured logging configuration
"""

__version__ = "0.1.0"

# Import config for backward compatibility
from .config import config

# Lazy imports to avoid circular dependencies
# Users should import from submodules directly:
#   from shared.types import Document, Chunk, Result, Option
#   from shared.rag.interfaces import Chunker, EmbeddingEncoder
#   from shared.blob_storage import BlobStorage, create_blob_storage

__all__ = [
    "__version__",
    "config",
]
