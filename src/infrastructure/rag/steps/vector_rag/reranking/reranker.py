"""Reranking interface for Vector RAG."""

from abc import ABC, abstractmethod
from typing import List, Tuple

from returns.result import Result


class Reranker(ABC):
    """
    Abstract base class for reranking algorithms.

    Rerankers take a list of (text, score) pairs and return them
    reordered by relevance to the query.
    """

    @abstractmethod
    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """
        Rerank texts based on relevance to the query.

        Args:
            query: The search query
            texts: List of text chunks to rerank
            scores: Corresponding similarity scores

        Returns:
            Reranked list of (text, score) tuples, ordered by relevance
        """
        pass
