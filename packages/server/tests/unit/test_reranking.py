"""Unit tests for reranking algorithms."""

import pytest

from src.rag.vector_rag.reranking import (
    BM25Reranker,
    CrossEncoderReranker,
    NoReranker,
    ReciprocalRankFusionReranker,
    create_reranker,
    get_available_rerankers,
)


class TestReranking:
    """Tests for reranking algorithms."""

    def test_no_reranker(self):
        """Test NoReranker returns results unchanged."""
        reranker = NoReranker()
        texts = ["text1", "text2", "text3"]
        scores = [0.9, 0.8, 0.7]

        result = reranker.rerank("query", texts, scores)
        assert result.is_ok()

        reranked = result.unwrap()
        assert len(reranked) == 3
        assert reranked[0] == ("text1", 0.9)
        assert reranked[1] == ("text2", 0.8)
        assert reranked[2] == ("text3", 0.7)

    def test_create_reranker_none(self):
        """Test creating NoReranker via factory."""
        reranker = create_reranker("none")
        assert isinstance(reranker, NoReranker)

    def test_create_reranker_cross_encoder(self):
        """Test creating CrossEncoderReranker via factory."""
        reranker = create_reranker("cross-encoder")
        assert isinstance(reranker, CrossEncoderReranker)
        assert reranker.model_name == "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def test_create_reranker_bm25(self):
        """Test creating BM25Reranker via factory."""
        reranker = create_reranker("bm25")
        assert isinstance(reranker, BM25Reranker)
        assert reranker.k1 == 1.5
        assert reranker.b == 0.75

    def test_create_reranker_rrf(self):
        """Test creating ReciprocalRankFusionReranker via factory."""
        reranker = create_reranker("rrf")
        assert isinstance(reranker, ReciprocalRankFusionReranker)
        assert reranker.k == 60

    def test_create_reranker_invalid(self):
        """Test creating invalid reranker type raises error."""
        with pytest.raises(ValueError, match="Unknown reranker type"):
            create_reranker("invalid_type")

    def test_get_available_rerankers(self):
        """Test getting list of available rerankers."""
        rerankers = get_available_rerankers()
        assert len(rerankers) == 4

        # Check that all expected rerankers are present
        values = [r["value"] for r in rerankers]
        assert "none" in values
        assert "cross-encoder" in values
        assert "bm25" in values
        assert "rrf" in values

        # Check structure
        for reranker in rerankers:
            assert "value" in reranker
            assert "label" in reranker
            assert "description" in reranker

    @pytest.mark.skip(reason="Requires sentence-transformers which may not be installed")
    def test_cross_encoder_reranker(self):
        """Test CrossEncoderReranker (skipped if dependencies not available)."""
        reranker = CrossEncoderReranker()
        texts = ["Python is a programming language", "Java is also a programming language", "Cats are animals"]
        scores = [0.8, 0.7, 0.3]

        result = reranker.rerank("programming language", texts, scores)
        # This will fail if sentence-transformers is not installed, which is expected
        if result.is_err():
            assert "sentence-transformers" in result.err()
        else:
            reranked = result.unwrap()
            assert len(reranked) == 3
            # Should reorder results based on cross-encoder scores

    @pytest.mark.skip(reason="Requires rank-bm25 and nltk which may not be installed")
    def test_bm25_reranker(self):
        """Test BM25Reranker (skipped if dependencies not available)."""
        reranker = BM25Reranker()
        texts = ["Python programming language", "Java programming language", "Cat animal"]
        scores = [0.8, 0.7, 0.3]

        result = reranker.rerank("programming language", texts, scores)
        # This will fail if rank-bm25/nltk are not installed, which is expected
        if result.is_err():
            assert "rank-bm25" in result.err() or "nltk" in result.err()
        else:
            reranked = result.unwrap()
            assert len(reranked) == 3
            # Should reorder results based on BM25 scores

    def test_reciprocal_rank_fusion_reranker(self):
        """Test ReciprocalRankFusionReranker."""
        reranker = ReciprocalRankFusionReranker()
        texts = ["text1", "text2", "text3"]
        scores = [0.9, 0.8, 0.7]

        result = reranker.rerank("query", texts, scores)
        assert result.is_ok()

        reranked = result.unwrap()
        assert len(reranked) == 3
        # For now, RRF just sorts by original scores
        assert reranked[0] == ("text1", 0.9)
        assert reranked[1] == ("text2", 0.8)
        assert reranked[2] == ("text3", 0.7)