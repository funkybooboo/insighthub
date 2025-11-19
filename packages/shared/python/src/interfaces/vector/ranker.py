"""Ranker interface for Vector RAG."""

from abc import ABC, abstractmethod

from shared.types import RetrievalResult


class Ranker(ABC):
    """
    Re-ranks retrieved chunks to improve relevance for LLM context.

    Can use cross-encoders, BM25, or other ranking algorithms.
    """

    @abstractmethod
    def rerank(
        self,
        candidates: list[RetrievalResult],
        query: str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """
        Re-rank retrieval candidates.

        Args:
            candidates: List of retrieved results
            query: Optional query string for cross-encoder ranking
            top_k: Optional limit for top-k results

        Returns:
            Re-ranked list of RetrievalResult
        """
        raise NotImplementedError
