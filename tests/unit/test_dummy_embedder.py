"""Unit tests for DummyEmbeddingEncoder.

Tests the dummy embedder used in testing without external dependencies.
"""

from src.infrastructure.rag.steps.vector_rag.embedding.dummy_embedder import DummyEmbeddingEncoder


class TestDummyEmbeddingEncoder:
    """Test dummy embedding encoder behavior."""

    def test_encode_single_text(self):
        """Test encoding a single text."""
        # Arrange
        embedder = DummyEmbeddingEncoder(dimension=3)

        # Act
        result = embedder.encode_one("Hello world")

        # Assert
        embedding = result.unwrap()
        assert len(embedding) == 3
        assert all(val == 0.1 for val in embedding)

    def test_encode_multiple_texts(self):
        """Test encoding multiple texts."""
        # Arrange
        embedder = DummyEmbeddingEncoder(dimension=5)
        texts = ["First text", "Second text", "Third text"]

        # Act
        result = embedder.encode(texts)

        # Assert
        embeddings = result.unwrap()
        assert len(embeddings) == 3
        assert all(len(emb) == 5 for emb in embeddings)
        assert all(all(val == 0.1 for val in emb) for emb in embeddings)

    def test_get_dimension(self):
        """Test getting embedding dimension."""
        # Arrange & Act
        embedder = DummyEmbeddingEncoder(dimension=128)

        # Assert
        assert embedder.get_dimension() == 128

    def test_get_model_name(self):
        """Test getting model name."""
        # Arrange & Act
        embedder = DummyEmbeddingEncoder()

        # Assert
        assert embedder.get_model_name() == "dummy-embedding-model"

    def test_default_dimension(self):
        """Test default dimension is 384."""
        # Arrange & Act
        embedder = DummyEmbeddingEncoder()

        # Assert
        assert embedder.get_dimension() == 384
        result = embedder.encode_one("test")
        embedding = result.unwrap()
        assert len(embedding) == 384
