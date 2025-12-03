"""Cross-encoder reranker implementation."""

from typing import List, Tuple

from returns.result import Failure, Result, Success

from .reranker import Reranker

try:
    from sentence_transformers import CrossEncoder

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    CrossEncoder = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class CrossEncoderReranker(Reranker):
    """
    Reranker using cross-encoder models for improved relevance scoring.

    Cross-encoders jointly encode query and document, providing
    more accurate relevance scores than bi-encoders.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the cross-encoder reranker.

        Args:
            model_name: HuggingFace model name for cross-encoder
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE or CrossEncoder is None:
            raise ImportError(
                "sentence-transformers is required for CrossEncoderReranker. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self._model: CrossEncoder | None = None

    def _load_model(self) -> None:
        """Lazy load the cross-encoder model."""
        if self._model is None and CrossEncoder is not None:
            self._model = CrossEncoder(self.model_name)

    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """
        Rerank using cross-encoder model.

        Args:
            query: The search query
            texts: List of text chunks to rerank
            scores: Original similarity scores (ignored by cross-encoder)

        Returns:
            Reranked list ordered by cross-encoder scores
        """
        try:
            self._load_model()

            if self._model is None:
                return Failure("Cross-encoder model not loaded")

            # Create query-document pairs
            pairs = [[query, text] for text in texts]

            # Get cross-encoder scores
            ce_scores = self._model.predict(pairs)

            # Combine with original scores (weighted average)
            combined_scores = []
            for ce_score, orig_score in zip(ce_scores, scores):
                # Weight cross-encoder more heavily (0.7) than original (0.3)
                combined = 0.7 * ce_score + 0.3 * orig_score
                combined_scores.append(combined)

            # Sort by combined score (descending)
            scored_items = list(zip(texts, combined_scores))
            scored_items.sort(key=lambda x: x[1], reverse=True)

            return Success(scored_items)

        except Exception as e:
            return Failure(f"Cross-encoder reranking failed: {str(e)}")
