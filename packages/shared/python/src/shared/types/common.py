"""Common type definitions used across the RAG system."""

from typing import Any, Union, Literal
from enum import Enum

# Union type for primitive values that can be stored in metadata
PrimitiveValue = Union[str, int, float, bool]

# Union type for metadata values that can be stored in metadata  
MetadataValue = Union[PrimitiveValue, list[PrimitiveValue], dict[str, PrimitiveValue]]


class DocumentStatus(str, Enum):
    """Document processing status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class ChunkStatus(str, Enum):
    """Chunk processing status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class ProcessingStage(str, Enum):
    """Document processing stage."""
    INGESTION = "ingestion"
    EMBEDDING = "embedding"
    GRAPH_BUILDING = "graph_building"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"