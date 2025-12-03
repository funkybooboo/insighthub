"""Reciprocal Rank Fusion (RRF) reranker implementation."""

from typing import List, Tuple

from returns.result import Failure, Result, Success

from .reranker import Reranker


class ReciprocalRankFusionReranker(Reranker):
    """
    Reranker using Reciprocal Rank Fusion (RRF) algorithm.

    RRF combines rankings from multiple sources without requiring
    score normalization. Effective for ensemble reranking.
    """

    def __init__(self, k: int = 60):
        """
        Initialize RRF reranker.

        Args:
            k: RRF k parameter (typically 60, smaller values favor top ranks more)
        """
        self.k = k

    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """
        Rerank using Reciprocal Rank Fusion.

        Since we only have one ranking (the original scores), this
        implementation sorts by original score. In practice, RRF
        would combine multiple rankings.

        Args:
            query: The search query (unused in this implementation)
            texts: List of text chunks to rerank
            scores: Original similarity scores

        Returns:
            Texts sorted by original scores (RRF would combine multiple rankings)
        """
        try:
            # For now, just sort by original scores
            # In a full implementation, this would combine multiple rankings
            scored_items = list(zip(texts, scores))
            scored_items.sort(key=lambda x: x[1], reverse=True)

            return Success(scored_items)

        except Exception as e:
            return Failure(f"RRF reranking failed: {str(e)}")
