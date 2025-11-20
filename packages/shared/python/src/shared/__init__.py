"""
InsightHub Shared Library.

This package contains shared types, interfaces, events, and utilities
used across the InsightHub server and worker processes.

Main exports:
- types: Core data types (Document, Chunk, GraphNode, etc.)
- interfaces: Abstract interfaces for RAG components
- components: Concrete implementations of interfaces (chunking, embeddings, etc.)
- events: Event schemas for RabbitMQ messaging
- orchestrators: High-level RAG pipeline orchestrators
- messaging: RabbitMQ publisher and consumer utilities
- logging: Structured logging configuration
- database: Database connection and session management
- storage: Blob storage interface and implementations
"""

__version__ = "0.1.0"

from . import (
    components,
    database,
    events,
    logging,
    messaging,
    storage,
    types,
)
from .rag import orchestrators, interfaces

__all__ = [
    "__version__",
    "types",
    "interfaces",
    "components",
    "events",
    "orchestrators",
    "messaging",
    "logging",
    "database",
    "storage",
]
