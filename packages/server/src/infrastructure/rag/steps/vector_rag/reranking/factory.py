"""Factory functions for creating reranking algorithms."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.vector_rag.reranking.reranker import (
    BM25Reranker,
    CrossEncoderReranker,
    NoReranker,
    ReciprocalRankFusionReranker,
    Reranker,
)

logger = create_logger(__name__)


class RerankerFactory:
    """Factory class for creating rerankers."""

    @staticmethod
    def create_reranker(reranker_type: str, **kwargs) -> Reranker:
        """Create a reranker instance. Alias for create_reranker function."""
        return create_reranker(reranker_type, **kwargs)


def create_reranker(reranker_type: str, **kwargs) -> Reranker:
    """
    Factory function to create rerankers from configuration.

    Args:
        reranker_type: Type of reranker to create
        **kwargs: Reranker-specific configuration

    Returns:
        Configured reranker instance

    Raises:
        ValueError: If reranker_type is not supported
    """
    reranker_type = reranker_type.lower()

    if reranker_type == "none":
        return NoReranker()
    elif reranker_type == "cross-encoder":
        model_name = kwargs.get("model_name", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        return CrossEncoderReranker(model_name=model_name)
    elif reranker_type == "bm25":
        k1 = kwargs.get("k1", 1.5)
        b = kwargs.get("b", 0.75)
        return BM25Reranker(k1=k1, b=b)
    elif reranker_type == "rrf":
        k = kwargs.get("k", 60)
        return ReciprocalRankFusionReranker(k=k)
    else:
        available = ["none", "cross-encoder", "bm25", "rrf"]
        raise ValueError(
            f"Unknown reranker type: {reranker_type}. "
            f"Available types: {', '.join(available)}"
        )


def get_available_rerankers() -> list[dict[str, str]]:
    """
    Get list of available reranker configurations.

    Returns:
        List of reranker info dictionaries with 'value', 'label', and 'description'
    """
    return [
        {
            "value": "none",
            "label": "No Reranking",
            "description": "Return results as-is from vector search"
        },
        {
            "value": "cross-encoder",
            "label": "Cross Encoder",
            "description": "Rerank using cross-encoder model for better relevance"
        },
        {
            "value": "bm25",
            "label": "BM25",
            "description": "Rerank using BM25 algorithm for keyword-based relevance"
        },
        {
            "value": "rrf",
            "label": "Reciprocal Rank Fusion",
            "description": "Combine multiple rankings using RRF algorithm"
        }
    ]