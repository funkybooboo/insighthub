"""RAG Options domain DTOs."""

from typing import List

from pydantic import BaseModel


class RagOption(BaseModel):
    """Single RAG option."""

    value: str
    description: str


class RagOptionsResponse(BaseModel):
    """Response DTO for available RAG options."""

    rag_types: List[RagOption]
    chunking_algorithms: List[RagOption]
    embedding_algorithms: List[RagOption]
    rerank_algorithms: List[RagOption]
    entity_extraction_algorithms: List[RagOption]
    relationship_extraction_algorithms: List[RagOption]
    clustering_algorithms: List[RagOption]
