"""Embedding-related event schemas."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EmbeddingGenerateEvent:
    """
    Published to trigger embedding generation for document chunks.

    Consumed by: Embeddings Worker
    """

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    embedding_model: str
    metadata: dict[str, Any]


@dataclass
class VectorIndexUpdatedEvent:
    """
    Published when vectors have been indexed in Qdrant.

    Consumed by: Server (for notifications, cache invalidation)
    """

    document_id: str
    workspace_id: str
    chunk_count: int
    collection_name: str
    metadata: dict[str, Any]
