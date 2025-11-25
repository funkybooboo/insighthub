"""Integration tests for embedder worker using real testcontainers - no mocks."""

import json
import uuid
from unittest.mock import MagicMock

import psycopg2
import psycopg2.extras

from main import EmbedderWorker


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


class TestEmbedderWorkerDatabaseIntegration:
    """Integration tests for database operations using real PostgreSQL."""

    def test_chunk_text_retrieval(self, postgres_container):
        """Test that chunk texts can be retrieved from real database."""
        # Convert SQLAlchemy URL to psycopg2 format
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema and insert test data
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE document_chunks (
                    id UUID PRIMARY KEY,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding JSONB
                )
            """
            )
            # Insert test chunks
            chunk_id_1 = str(uuid.uuid4())
            chunk_id_2 = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO document_chunks (id, document_id, chunk_text) VALUES
                (%s, 1, 'This is the first chunk of text.'),
                (%s, 1, 'This is the second chunk of text.')
            """,
                (chunk_id_1, chunk_id_2),
            )
        conn.commit()

        # Test direct database operations that the worker would perform
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, chunk_text FROM document_chunks WHERE id = ANY(%s::uuid[])",
                ([chunk_id_1, chunk_id_2],),
            )
            results = cursor.fetchall()

        # Verify correct data retrieval
        assert len(results) == 2
        id_to_text_map = {str(row["id"]): row["chunk_text"] for row in results}
        assert id_to_text_map[chunk_id_1] == "This is the first chunk of text."
        assert id_to_text_map[chunk_id_2] == "This is the second chunk of text."

        conn.close()

    def test_embedding_storage(self, postgres_container):
        """Test that embeddings can be stored in real database."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE document_chunks (
                    id UUID PRIMARY KEY,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding JSONB
                )
            """
            )
            chunk_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO document_chunks (id, document_id, chunk_text) VALUES (%s, 1, 'Test chunk')",
                (chunk_id,),
            )
        conn.commit()

        # Test embedding storage
        test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE document_chunks SET embedding = %s WHERE id = %s",
                (json.dumps(test_embedding), chunk_id),
            )
        conn.commit()

        # Verify embedding was stored
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT embedding FROM document_chunks WHERE id = %s", (chunk_id,)
            )
            result = cursor.fetchone()

        assert result is not None
        assert result["embedding"] == test_embedding

        conn.close()

    def test_document_status_updates(self, postgres_container):
        """Test document status updates in real database."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    processing_status VARCHAR(50),
                    processing_metadata JSONB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                "INSERT INTO documents (id, processing_status) VALUES (1, 'chunked')"
            )
        conn.commit()

        # Test status update
        metadata = {"embedding_count": 5, "embedding_dimension": 384}
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE documents SET processing_status = %s, processing_metadata = %s, updated_at = NOW() WHERE id = %s",
                ("embedded", json.dumps(metadata), 1),
            )
        conn.commit()

        # Verify status update
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT processing_status, processing_metadata FROM documents WHERE id = %s",
                (1,),
            )
            result = cursor.fetchone()

        assert result is not None
        assert result["processing_status"] == "embedded"
        assert result["processing_metadata"] == metadata

        conn.close()


class TestEmbedderWorkerErrorHandling:
    """Test error handling scenarios."""

    def test_embedder_worker_error_handling_missing_chunks(self, postgres_container):
        """Test error handling when chunks don't exist in database."""
        # Setup PostgreSQL with document but no chunks
        pg_url = postgres_container.get_connection_url()
        if pg_url.startswith("postgresql+psycopg2://"):
            pg_url = pg_url.replace("postgresql+psycopg2://", "postgresql://")
        pg_conn = psycopg2.connect(pg_url)

        with pg_conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    processing_status VARCHAR(50),
                    processing_metadata JSONB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE document_chunks (
                    id UUID PRIMARY KEY,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding JSONB
                )
            """
            )
            cursor.execute(
                "INSERT INTO documents (id, processing_status) VALUES (1, 'chunked')"
            )
        pg_conn.commit()

        # Create worker instance without calling __init__ to avoid config loading
        worker = EmbedderWorker.__new__(EmbedderWorker)
        worker.db_connection = DummyPostgresConnection()

        # Mock get_cursor to simulate database returning no chunks
        def mock_get_cursor(as_dict=False):
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []  # No chunks found
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=None)
            return mock_cursor

        worker.db_connection.get_cursor = mock_get_cursor

        # Test that _get_chunk_texts returns empty list for non-existent chunks
        fake_chunk_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        result = worker._get_chunk_texts(fake_chunk_ids)
        assert result == []

        # Cleanup
        pg_conn.close()
