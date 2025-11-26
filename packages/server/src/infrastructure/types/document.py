"""Document and chunk types for RAG processing."""

from dataclasses import dataclass, field

from src.infrastructure.types.common import MetadataDict


@dataclass
class Document:
    """
    Document type for RAG processing.

    This is distinct from the database Document model (infrastructure/models/document.py).
    This type represents a parsed document ready for RAG processing (chunking, embedding).
    """

    id: str
    workspace_id: str
    title: str
    content: str
    metadata: MetadataDict = field(default_factory=dict)


@dataclass
class Chunk:
    """
    Text chunk extracted from a document.

    Represents a semantically meaningful segment of text with metadata about
    its position and relationship to the source document.
    """

    id: str
    document_id: str
    text: str
    metadata: MetadataDict = field(default_factory=dict)
