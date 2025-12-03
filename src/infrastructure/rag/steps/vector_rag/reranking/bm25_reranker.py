"""BM25 reranker implementation."""

from typing import List, Tuple

from returns.result import Failure, Result, Success

from .reranker import Reranker


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

            # Tokenize query and document
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

            return Success(scored_items)

        except ImportError:
            return Failure(
                "rank-bm25 and nltk are required for BM25Reranker. "
                "Install with: pip install rank-bm25 nltk"
            )
        except Exception as e:
            return Failure(f"BM25 reranking failed: {str(e)}")
