"""Dummy implementations for unit testing."""

from unittest.mock import MagicMock

from shared.documents.embedding.vector_embedding_encoder import \
    VectorEmbeddingEncoder
from shared.types.result import Ok
from shared.worker.worker import Worker


class DummyEmbeddingEncoder(VectorEmbeddingEncoder):
    """Dummy embedding encoder for testing."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def encode(self, texts):
        """Return fixed embeddings for testing."""
        return Ok([[0.1, 0.2, 0.3] * (self._dimension // 3) for _ in texts])

    def encode_one(self, text: str):
        """Return fixed embedding for single text."""
        return Ok([0.1, 0.2, 0.3] * (self._dimension // 3))

    def get_dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def get_model_name(self) -> str:
        """Return model name."""
        return "dummy-embedding-model"


class DummyPostgresConnection:
    """Dummy PostgreSQL connection for testing."""

    def __init__(self, db_url: str = "dummy://"):
        self.db_url = db_url
        self.connection = MagicMock()
        self._test_data = {"document_chunks": {}, "documents": {}}

    def connect(self) -> None:
        """Mock connect."""
        pass

    def close(self) -> None:
        """Mock close."""
        pass

    def commit(self) -> None:
        """Mock commit."""
        pass

    def rollback(self) -> None:
        """Mock rollback."""
        pass

    def get_cursor(self, as_dict: bool = False):
        """Return mock cursor that acts as context manager."""
        cursor = MagicMock()
        if as_dict:
            # Mock RealDictCursor behavior
            cursor.fetchall.return_value = []
            cursor.fetchone.return_value = None
        # Make it a context manager
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=None)
        return cursor


class DummyWorker(Worker):
    """Dummy worker for testing."""

    def __init__(self):
        # Don't call super().__init__ to avoid RabbitMQ setup
        self._worker_name = "dummy"
        self._consumer = MagicMock()

    def process_event(self, event_data):
        """Mock process event."""
        pass

    def publish_event(self, routing_key: str, event):
        """Mock publish event."""
        pass

    def start(self):
        """Mock start."""
        pass

    def stop(self):
        """Mock stop."""
        pass
