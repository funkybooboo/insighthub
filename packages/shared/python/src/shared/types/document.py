"""Document and chunk data types."""

from dataclasses import dataclass

from shared.types.common import MetadataDict, PrimitiveValue


@dataclass
class Document:
    """
    Represents a document in the RAG system.

    Attributes:
        id: Unique identifier for the document
        workspace_id: Workspace or tenant identifier
        title: Optional human-readable title
        content: Raw textual content of the document
        metadata: Metadata dictionary (author, source, timestamps, etc.)
    """

    id: str
    workspace_id: str
    title: str | None
    content: str
    metadata: MetadataDict
    chunk_count: int | None = None


@dataclass
class Chunk:
    """
    Represents a chunked segment of a Document.

    Attributes:
        id: Unique identifier for the chunk
        document_id: Identifier of the source document
        text: Textual content of the chunk
        metadata: Chunk-level metadata (offset, tokenizer info, provenance, etc.)
        vector: Optional embedding vector assigned during indexing
    """

    id: str
    document_id: str
    text: str
    metadata: dict[str, PrimitiveValue]
    vector: list[float] | None = None
