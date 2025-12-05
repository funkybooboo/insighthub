"""RAG Options domain service."""

from typing import List

from src.domains.rag_options.dtos import RagOption
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import (
    get_chunking_options,
    get_embedding_options,
    get_graph_clustering_options,
    get_graph_entity_extraction_options,
    get_graph_relationship_extraction_options,
    get_rag_type_options,
    get_reranking_options,
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
        chunking = [RagOption(**opt) for opt in get_chunking_options()]
        embedding = [RagOption(**opt) for opt in get_embedding_options()]
        rerank = [RagOption(**opt) for opt in get_reranking_options()]
        entity_extraction = [RagOption(**opt) for opt in get_graph_entity_extraction_options()]
        relationship_extraction = [
            RagOption(**opt) for opt in get_graph_relationship_extraction_options()
        ]
        clustering = [RagOption(**opt) for opt in get_graph_clustering_options()]

        return (
            rag_types,
            chunking,
            embedding,
            rerank,
            entity_extraction,
            relationship_extraction,
            clustering,
        )
