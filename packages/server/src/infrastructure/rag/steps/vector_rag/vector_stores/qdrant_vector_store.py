"""Qdrant implementation of VectorStore interface (adapter pattern)."""

from src.infrastructure.logger import create_logger
from typing import List, Tuple

from src.infrastructure.types.common import MetadataDict
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

    def add(self, chunks: List[Chunk]) -> None:
        """
        Add chunks to the vector store.

        Converts Chunk objects to vectors and metadata, then vector_stores them in
        the underlying vector database. Each chunk must have an embedding.

        Args:
            chunks: List of chunks to add (must have embeddings)

        Raises:
            ValueError: If any chunk is missing an embedding
            VectorStoreError: If adding chunks fails
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        # Validate all chunks have vectors (embeddings)
        missing_vectors = [c.id for c in chunks if c.vector is None]
        if missing_vectors:
            raise ValueError(
                f"Chunks missing vectors: {missing_vectors[:5]}"
                f"{' and more...' if len(missing_vectors) > 5 else ''}"
            )

        # Convert chunks to (id, vector, metadata) tuples
        items = []
        for chunk in chunks:
            chunk_id = chunk.id
            vector = chunk.vector  # type: ignore  # Already validated above
            metadata: MetadataDict = {
                "document_id": chunk.document_id,
                "text": chunk.text,
                **chunk.metadata,  # Include any additional metadata
            }
            items.append((chunk_id, vector, metadata))

        # Batch upsert to database
        logger.info(f"Adding {len(items)} chunks to vector store")
        self.db.upsert_batch(items)

    def search(
        self, query_embedding: List[float], top_k: int = 5
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
                k: v
                for k, v in metadata.items()
                if k not in ("document_id", "text")
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
