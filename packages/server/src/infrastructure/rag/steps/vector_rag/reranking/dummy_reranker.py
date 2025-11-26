"""Dummy reranker for testing."""

from typing import List, Tuple

from src.infrastructure.types.result import Ok
from src.infrastructure.rag.steps.vector_rag.reranking.reranker import Reranker


class DummyReranker(Reranker):
    """
    Dummy reranker that returns results unchanged.

    Used for testing and as a baseline.
    """

    def rerank(
        self,
        query: str,
        texts: List[str],
        scores: List[float]
    ) -> Ok[List[Tuple[str, float]]]:
        """Return texts and scores unchanged."""
        return Ok(list(zip(texts, scores)))