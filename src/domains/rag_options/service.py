"""RAG Options domain service."""

from typing import List

from src.domains.rag_options.dtos import RagOption
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import (
    get_chunking_algorithm_options,
    get_clustering_algorithm_options,
    get_embedding_algorithm_options,
    get_entity_extraction_algorithm_options,
    get_rag_type_options,
    get_relationship_extraction_algorithm_options,
    get_rerank_algorithm_options,
)

logger = create_logger(__name__)


class RagOptionsService:
    """Service for querying available RAG options."""

    def get_all_options(
        self,
    ) -> tuple[
        List[RagOption],
        List[RagOption],
        List[RagOption],
        List[RagOption],
        List[RagOption],
        List[RagOption],
        List[RagOption],
    ]:
        """Get all available RAG options.

        Returns:
            Tuple of (rag_types, chunking, embedding, rerank, entity_extraction,
                     relationship_extraction, clustering)
        """
        rag_types = [RagOption(**opt) for opt in get_rag_type_options()]
        chunking = [RagOption(**opt) for opt in get_chunking_algorithm_options()]
        embedding = [RagOption(**opt) for opt in get_embedding_algorithm_options()]
        rerank = [RagOption(**opt) for opt in get_rerank_algorithm_options()]
        entity_extraction = [RagOption(**opt) for opt in get_entity_extraction_algorithm_options()]
        relationship_extraction = [
            RagOption(**opt) for opt in get_relationship_extraction_algorithm_options()
        ]
        clustering = [RagOption(**opt) for opt in get_clustering_algorithm_options()]

        return (
            rag_types,
            chunking,
            embedding,
            rerank,
            entity_extraction,
            relationship_extraction,
            clustering,
        )
