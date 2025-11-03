"""
Qdrant Vector Store - Local vector database that runs in Docker
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.rag.types import Metadata, SearchResult, Stats, Vector
from src.rag.stores.vector.base import VectorStore


class QdrantVectorStore(VectorStore):
    """
    Local vector store using Qdrant (runs in Docker).
    Drop-in replacement for Pinecone that runs completely locally.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "rag_collection",
        dimension: int = 768,
        metric: str = "cosine",
    ):
        """
        Initialize Qdrant vector store.

        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection
            dimension: Dimensionality of vectors
            metric: Distance metric (cosine, euclidean, or dot)
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.dimension = dimension

        # Map metric names
        metric_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT,
            "dotproduct": Distance.DOT,
        }
        self.metric = metric_map.get(metric.lower(), Distance.COSINE)

        # Create collection if it doesn't exist
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=self.metric),
            )

    def add(self, vectors: list[Vector], ids: list[str], metadata: list[Metadata]) -> None:
        """
        Add vectors to the store.

        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs
            metadata: List of metadata dictionaries
        """
        points = []
        for i in range(len(vectors)):
            # Convert id to integer hash if it's a string
            point_id = hash(ids[i]) % (2**63)  # Ensure positive integer within range

            point = PointStruct(
                id=point_id, vector=vectors[i], payload={**metadata[i], "original_id": ids[i]}
            )
            points.append(point)

        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)

    def search(
        self, query_vector: Vector, top_k: int = 5, filter: Metadata | None = None
    ) -> list[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding
            top_k: Number of results
            filter: Optional metadata filter

        Returns:
            List of matches with id, score, and metadata
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter,
        )

        matches: list[SearchResult] = []
        for result in results:
            payload = result.payload or {}
            matches.append(
                {
                    "id": payload.get("original_id", str(result.id)),
                    "score": result.score,
                    "metadata": payload,
                }
            )

        return matches

    def delete_all(self) -> None:
        """Delete all vectors from the collection."""
        # Recreate the collection (faster than deleting points)
        self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.dimension, distance=self.metric),
        )

    def get_stats(self) -> Stats:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {"total_vector_count": info.points_count, "vectors_count": info.vectors_count}

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"QdrantVectorStore(collection={self.collection_name}, vectors={stats.get('total_vector_count', 0)})"
