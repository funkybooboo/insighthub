"""Qdrant implementation of VectorStore interface (adapter pattern)."""

from typing import List, Tuple

from src.infrastructure.logger import create_logger
from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.document import Chunk

from .qdrant_vector_database import QdrantVectorDatabase
from .vector_store import VectorStore

logger = create_logger(__name__)


class QdrantVectorStore(VectorStore):
    """
    Adapter that implements VectorStore interface using QdrantVectorDatabase.

    This adapter bridges the high-level VectorStore interface (which works with
    Chunk objects) and the low-level VectorDatabase interface (which works with
    raw vectors and metadata).

    Example:
        db = QdrantVectorDatabase(url="http://localhost:6333", collection_name="docs")
        store = QdrantVectorStore(db)
        store.add(chunks)
        results = store.search(query_embedding, top_k=5)
    """

    def __init__(self, vector_database: QdrantVectorDatabase) -> None:
        """
        Initialize QdrantVectorStore with a VectorDatabase backend.

        Args:
            vector_database: The underlying vector database implementation
        """
        self.db = vector_database

    def add(self, vectors: List[List[float]], ids: List[str], payloads: List[MetadataDict]) -> None:
        """
        Add vectors to the vector store.

        Args:
            vectors: List of vector embeddings
            ids: List of unique IDs for the vectors
            payloads: List of metadata payloads for the vectors

        Raises:
            VectorStoreError: If adding vectors fails
        """
        if not vectors:
            logger.warning("No vectors to add")
            return

        # Validate input lengths match
        if len(vectors) != len(ids) or len(vectors) != len(payloads):
            raise ValueError(
                f"Input lengths don't match: vectors={len(vectors)}, ids={len(ids)}, payloads={len(payloads)}"
            )

        # Convert to items format expected by database
        items = []
        for vector, id_, payload in zip(vectors, ids, payloads):
            items.append((id_, vector, payload))

        # Batch upsert to database
        logger.info(f"Adding {len(items)} vectors to vector store")
        self.db.upsert_batch(items)

    def search(
        self, query_embedding: List[float], top_k: int = 5, filters: FilterDict | None = None
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks in the vector store.

        Args:
            query_embedding: The embedding of the query
            top_k: The number of similar chunks to return

        Returns:
            A list of tuples, where each tuple contains a chunk and its similarity score

        Raises:
            VectorStoreError: If searching fails
        """
        # Perform similarity search in database
        results = self.db.similarity_search(vector=query_embedding, top_k=top_k)

        # Convert RetrievalResult objects back to (Chunk, score) tuples
        chunk_results: List[Tuple[Chunk, float]] = []
        for result in results:
            # Extract chunk data from metadata
            metadata = result.payload
            document_id = str(metadata.get("document_id", ""))
            text = str(metadata.get("text", ""))

            # Remove our internal fields to get original metadata
            original_metadata = {
                k: v for k, v in metadata.items() if k not in ("document_id", "text")
            }

            # Reconstruct chunk (using types.document.Chunk)
            chunk = Chunk(
                id=result.id,
                document_id=document_id,
                text=text,
                metadata=original_metadata,  # type: ignore  # Metadata types are flexible
                vector=None,  # Vector not needed for retrieval results
            )

            chunk_results.append((chunk, result.score))

        logger.info(f"Found {len(chunk_results)} similar chunks")
        return chunk_results

    def clear(self) -> None:
        """
        Clear all vectors from the collection.

        This recreates the collection, effectively deleting all stored vectors.

        Raises:
            VectorStoreError: If clearing fails
        """
        logger.warning(f"Clearing all vectors from collection: {self.db.collection_name}")

        # Get all vector IDs and delete them
        # QdrantVectorDatabase doesn't have a clear() method, so we need to
        # recreate the collection via the client
        try:
            self.db.client.delete_collection(collection_name=self.db.collection_name)
            self.db._ensure_collection_exists()
            logger.info("Vector store cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise
