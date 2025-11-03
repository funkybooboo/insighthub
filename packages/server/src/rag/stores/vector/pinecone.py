"""
Vector Store wrapper for Pinecone
Simple interface for storing and retrieving document embeddings
"""

import time

from src.rag.types import Metadata, SearchResult, Stats, Vector
from src.rag.stores.vector.base import VectorStore

try:
    from pinecone import Pinecone, ServerlessSpec  # type: ignore[import-not-found]
except ImportError as e:
    raise ImportError("Pinecone is not installed. Install it with: pip install pinecone") from e


class PineconeVectorStore(VectorStore):
    """
    Simple wrapper around Pinecone for document storage and retrieval.
    """

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
    ):
        """
        Initialize the vector store.

        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            dimension: Dimensionality of the embeddings
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider
            region: Cloud region
        """
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        # Create index if it doesn't exist
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region),
            )
            # Wait for index to be ready
            while not self.pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

        self.index = self.pc.Index(index_name)

    def add(self, vectors: list[Vector], ids: list[str], metadata: list[Metadata]) -> None:
        """
        Add vectors to the store.

        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs for each vector
            metadata: List of metadata dictionaries
        """
        # Prepare vectors for upsert
        vectors_to_upsert = [(ids[i], vectors[i], metadata[i]) for i in range(len(vectors))]

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i : i + batch_size]
            self.index.upsert(vectors=batch)

    def search(
        self, query_vector: Vector, top_k: int = 5, filter: Metadata | None = None
    ) -> list[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: The query embedding
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of matches with id, score, and metadata
        """
        results = self.index.query(
            vector=query_vector, top_k=top_k, include_metadata=True, filter=filter
        )

        return [
            {"id": match["id"], "score": match["score"], "metadata": match.get("metadata", {})}
            for match in results["matches"]
        ]

    def delete_all(self) -> None:
        """Delete all vectors from the index."""
        self.index.delete(delete_all=True)

    def get_stats(self) -> Stats:
        """Get index statistics."""
        return self.index.describe_index_stats()  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"PineconeVectorStore(index={self.index_name}, vectors={stats.get('total_vector_count', 0)})"
