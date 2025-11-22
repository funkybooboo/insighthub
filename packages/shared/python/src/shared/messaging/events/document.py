"""Document-related event schemas."""

from dataclasses import dataclass

from shared.types.common import MetadataDict


@dataclass
class DocumentUploadedEvent:
    """
    Published when a document is uploaded and stored.

    Consumed by: Ingestion Worker
    """

    document_id: str
    workspace_id: str
    filename: str
    storage_path: str
    metadata: MetadataDict


@dataclass
class DocumentChunksReadyEvent:
    """
    Published when a document has been chunked and chunks are stored in the database.

    Consumed by: Embeddings Worker, Graph Worker
    """

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    chunk_count: int
    metadata: MetadataDict


@dataclass
class DocumentGraphBuildEvent:
    """
    Published to trigger graph construction for a document.

    Consumed by: Graph Worker
    """

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    metadata: MetadataDict
