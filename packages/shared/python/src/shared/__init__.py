"""
InsightHub Shared Library.

This package contains shared types, interfaces, events, and utilities
used across the InsightHub server and worker processes.

Main exports:
- types: Core data types (Document, Chunk, GraphNode, etc.)
- interfaces: Abstract interfaces for RAG components
- events: Event schemas for RabbitMQ messaging
- orchestrators: High-level RAG pipeline orchestrators
- messaging: RabbitMQ publisher and consumer utilities
- logging: Structured logging configuration
- database: Database connection and session management
- storage: Blob storage interface and implementations
"""

__version__ = "0.1.0"

# Core modules are available via their respective imports:
#   from shared.types import Document, Chunk
#   from shared.events import DocumentUploadedEvent
#   from shared.interfaces.vector import EmbeddingEncoder
#   from shared.messaging import RabbitMQPublisher, WorkerBase
#   from shared.logging import setup_logging, get_logger
#   from shared.database import get_db, get_engine
#   from shared.storage import BlobStorage, MinIOBlobStorage

__all__ = ["__version__"]
