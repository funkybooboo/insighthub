"""Result ranking interface for reordering retrieved vectors by relevance."""

from abc import ABC, abstractmethod
from typing import Any, List

from shared.types.retrieval import RetrievalResult


class Ranker(ABC):
    """
    Interface for re-ranking retrieved vectors to improve relevance.
    
    Implementations can use:
    - Cross-encoders
    - BM25 scoring
    - Learning-to-rank models
    - Custom scoring functions
    """

    @abstractmethod
    def rerank(self, candidates: List[RetrievalResult], query: str | None = None, top_k: int | None = None) -> List[RetrievalResult]:
        """
        Re-rank a list of retrieved results.

        Args:
            candidates: List of retrieved results to re-rank
            query: Optional query string for cross-encoder scoring
            top_k: Optional number of top results to return

        Returns:
            List[RetrievalResult]: Re-ranked results

        Raises:
            RankingError: If re-ranking fails
        """
        pass