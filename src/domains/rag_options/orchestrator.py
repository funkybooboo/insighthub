"""RAG Options domain orchestrator."""

from returns.result import Result, Success

from src.domains.rag_options.dtos import RagOptionsResponse
from src.domains.rag_options.service import RagOptionsService


class RagOptionsOrchestrator:
    """Orchestrates RAG options query operations."""

    def __init__(self, service: RagOptionsService):
        """Initialize orchestrator with service."""
        self.service = service

    def get_all_options(self) -> Result[RagOptionsResponse, None]:
        """Get all available RAG options.

        Returns:
            Result with RagOptionsResponse
        """
        (
            rag_types,
            chunking,
            embedding,
            rerank,
            entity_extraction,
            relationship_extraction,
            clustering,
        ) = self.service.get_all_options()

        response = RagOptionsResponse(
            rag_types=rag_types,
            chunking_algorithms=chunking,
            embedding_algorithms=embedding,
            rerank_algorithms=rerank,
            entity_extraction_algorithms=entity_extraction,
            relationship_extraction_algorithms=relationship_extraction,
            clustering_algorithms=clustering,
        )

        return Success(response)
