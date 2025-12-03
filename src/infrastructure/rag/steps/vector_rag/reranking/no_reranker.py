"""No-op reranker implementation."""

from typing import List, Tuple

from returns.result import Result, Success

from .reranker import Reranker


class NoReranker(Reranker):
    """
    No-op reranker that returns results unchanged.

    Useful as a baseline and for cases where reranking is not needed.
    """

    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """Return texts and scores unchanged."""
        return Success(list(zip(texts, scores)))
