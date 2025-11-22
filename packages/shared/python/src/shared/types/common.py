"""Common type definitions used across the RAG system."""

from enum import Enum

# Primitive values that can be stored/serialized
PrimitiveValue = str | int | float | bool | None

# Metadata value types - nested structures of primitives
MetadataValue = (
    PrimitiveValue
    | list[PrimitiveValue]
    | dict[str, PrimitiveValue]
    | list["MetadataDict"]
)

# Metadata dictionary type - replaces dict[str, Any] for metadata
MetadataDict = dict[str, PrimitiveValue | list[PrimitiveValue] | dict[str, PrimitiveValue]]

# JSON-serializable value type - for API responses and payloads
JsonValue = (
    str
    | int
    | float
    | bool
    | None
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)

# Payload dictionary - replaces dict[str, Any] for event payloads
PayloadDict = dict[str, JsonValue]

# Properties dictionary for graph nodes/edges
PropertiesDict = dict[str, PrimitiveValue]

# Filter dictionary for queries
FilterDict = dict[str, str | int | float | bool]

# Health check response type
HealthStatus = dict[str, str | bool]


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