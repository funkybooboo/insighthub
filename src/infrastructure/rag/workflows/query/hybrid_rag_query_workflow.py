"""Hybrid RAG query workflow implementation."""

from typing import Optional

from src.infrastructure.rag.workflows.query.graph_rag_query_workflow import GraphRagQueryWorkflow
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow
from src.infrastructure.rag.workflows.query.vector_rag_query_workflow import VectorRagQueryWorkflow
from src.infrastructure.types.common import FilterDict
from src.infrastructure.types.rag import ChunkData


class HybridRagQueryWorkflow(QueryWorkflow):
    """Hybrid RAG query workflow using Reciprocal Rank Fusion.

    Reciprocal Rank Fusion (RRF) is a method for combining ranked lists from multiple
    sources. It gives higher scores to items that appear early in multiple lists.

    RRF score for an item = Σ (1 / (k + rank_i)) for each list i where the item appears
    where k is a constant (typically 60) to reduce the impact of high-ranked items.
    """

    def __init__(
        self,
        vector_workflow: VectorRagQueryWorkflow,
        graph_workflow: GraphRagQueryWorkflow,
        rrf_k: int = 60,
    ):
        """Initialize the Hybrid RAG query workflow.

        Args:
            vector_workflow: Vector RAG query workflow
            graph_workflow: Graph RAG query workflow
            rrf_k: Constant for Reciprocal Rank Fusion (default: 60)
        """
        self.vector_workflow = vector_workflow
        self.graph_workflow = graph_workflow
        self.rrf_k = rrf_k

    def _reciprocal_rank_fusion(
        self,
        vector_chunks: list[ChunkData],
        graph_chunks: list[ChunkData],
    ) -> list[ChunkData]:
        """Merge and re-rank chunks using Reciprocal Rank Fusion.

        Args:
            vector_chunks: Chunks from vector RAG (already ranked)
            graph_chunks: Chunks from graph RAG (already ranked)

        Returns:
            Merged and re-ranked chunks
        """
        # Build RRF scores for all chunks
        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, ChunkData] = {}

        # Process vector chunks (lower index = higher rank)
        for rank, chunk in enumerate(vector_chunks):
            chunk_id = chunk.chunk_id
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk

        # Process graph chunks (lower index = higher rank)
        for rank, chunk in enumerate(graph_chunks):
            chunk_id = chunk.chunk_id
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk

        # Sort by RRF score (descending)
        sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        # Return chunks in RRF-ranked order
        return [chunk_map[chunk_id] for chunk_id in sorted_chunk_ids]

    def execute(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[FilterDict] = None,
    ) -> list[ChunkData]:
        """Execute the Hybrid RAG query workflow with Reciprocal Rank Fusion.

        Args:
            query_text: Query text
            top_k: Number of results to return from each source (will be fused)
            filters: Optional filters

        Returns:
            Re-ranked chunks using RRF
        """
        # Get results from both sources
        # Request more results from each source since we'll be fusing them
        source_top_k = top_k * 2  # Get 2x results from each source for better fusion
        vector_chunks = self.vector_workflow.execute(query_text, source_top_k, filters)
        graph_chunks = self.graph_workflow.execute(query_text, source_top_k, filters)

        # Fuse results using Reciprocal Rank Fusion
        fused_chunks = self._reciprocal_rank_fusion(vector_chunks, graph_chunks)

        # Return top_k results after fusion
        return fused_chunks[:top_k]
