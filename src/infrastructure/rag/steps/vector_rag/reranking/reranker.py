"""Reranking interfaces and implementations for Vector RAG."""

from abc import ABC, abstractmethod
from typing import List, Tuple

from src.infrastructure.types.result import Err, Ok, Result


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


class NoReranker(Reranker):
    """
    No-op reranker that returns results unchanged.

    Useful as a baseline and for cases where reranking is not needed.
    """

    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """Return texts and scores unchanged."""
        return Ok(list(zip(texts, scores)))


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
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """Lazy load the cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for CrossEncoderReranker. "
                    "Install with: pip install sentence-transformers"
                )

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

            return Ok(scored_items)

        except Exception as e:
            return Err(f"Cross-encoder reranking failed: {str(e)}")


class BM25Reranker(Reranker):
    """
    Reranker using BM25 algorithm for keyword-based relevance.

    BM25 is effective for sparse, keyword-focused queries and
    can complement semantic similarity scores.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 reranker.

        Args:
            k1: BM25 k1 parameter (term frequency saturation)
            b: BM25 b parameter (document length normalization)
        """
        self.k1 = k1
        self.b = b

    def rerank(
        self, query: str, texts: List[str], scores: List[float]
    ) -> Result[List[Tuple[str, float]], str]:
        """
        Rerank using BM25 algorithm combined with original scores.

        Args:
            query: The search query
            texts: List of text chunks to rerank
            scores: Original similarity scores

        Returns:
            Reranked list combining BM25 and original scores
        """
        try:
            import nltk
            from nltk.tokenize import word_tokenize
            from rank_bm25 import BM25Okapi

            # Ensure NLTK punkt is available
            try:
                nltk.data.find("tokenizers/punkt")
            except LookupError:
                nltk.download("punkt", quiet=True)

            # Tokenize query and documents
            query_tokens = word_tokenize(query.lower())
            doc_tokens = [word_tokenize(text.lower()) for text in texts]

            # Create BM25 model
            bm25 = BM25Okapi(doc_tokens, k1=self.k1, b=self.b)

            # Get BM25 scores
            bm25_scores = bm25.get_scores(query_tokens)

            # Normalize BM25 scores to 0-1 range
            if bm25_scores.max() > bm25_scores.min():
                bm25_scores = (bm25_scores - bm25_scores.min()) / (
                    bm25_scores.max() - bm25_scores.min()
                )

            # Combine BM25 with original scores
            combined_scores = []
            for bm25_score, orig_score in zip(bm25_scores, scores):
                # Weight BM25 and original scores equally
                combined = 0.5 * bm25_score + 0.5 * orig_score
                combined_scores.append(combined)

            # Sort by combined score
            scored_items = list(zip(texts, combined_scores))
            scored_items.sort(key=lambda x: x[1], reverse=True)

            return Ok(scored_items)

        except ImportError:
            return Err(
                "rank-bm25 and nltk are required for BM25Reranker. "
                "Install with: pip install rank-bm25 nltk"
            )
        except Exception as e:
            return Err(f"BM25 reranking failed: {str(e)}")


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

            return Ok(scored_items)

        except Exception as e:
            return Err(f"RRF reranking failed: {str(e)}")
