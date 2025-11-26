"""Qdrant vector database implementation."""

import uuid
from typing import Any

from src.infrastructure.logger import create_logger
from src.infrastructure.types.retrieval import RetrievalResult

from .vector_database import VectorDatabase

logger = create_logger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import (
        Distance,
        FieldCondition,
        Filter,
        MatchValue,
        PointIdsList,
        PointStruct,
        VectorParams,
    )

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    models = None
    Distance = None
    VectorParams = None
    PointStruct = None
    Filter = None
    FieldCondition = None
    MatchValue = None
    PointIdsList = None


class QdrantVectorDatabase(VectorDatabase):
    """
    Qdrant implementation of VectorDatabase.

    Provides vector storage and similarity search using the Qdrant vector database.
    Supports filtering, batch operations, and metadata storage.

    Example:
        db = QdrantVectorDatabase(
            url="http://localhost:6333",
            collection_name="documents",
            vector_size=384
        )
        db.upsert("chunk_1", [0.1, 0.2, ...], {"source": "doc.pdf"})
        results = db.similarity_search([0.1, 0.2, ...], top_k=5)
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "documents",
        vector_size: int = 384,
        distance: str = "cosine",
        api_key: str | None = None,
    ) -> None:
        """
        Initialize Qdrant vector database.

        Args:
            url: Qdrant server URL
            collection_name: Collection to use for vectors
            vector_size: Dimension of vectors to store
            distance: Distance metric ("cosine", "euclidean", "dot")
            api_key: Optional API key for Qdrant Cloud
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not installed. Please run: pip install qdrant-client")

        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.api_key = api_key

        # Map distance string to Qdrant Distance enum
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT,
        }
        self._distance = distance_map.get(distance.lower(), Distance.COSINE)

        # Initialize client
        self._client = QdrantClient(url=url, api_key=api_key)

        # Ensure collection exists
        self._ensure_collection()

        logger.info(f"Connected to Qdrant at {url}, collection: {collection_name}")

    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self._client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self._distance,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

    def _string_to_uuid(self, string_id: str) -> str:
        """
        Convert a string ID to a UUID format for Qdrant.

        Qdrant requires either UUID or integer IDs. We use UUID5 to create
        deterministic UUIDs from string IDs.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, string_id))

    def _build_filter(self, filters: dict[str, str | int | float | bool] | None) -> Filter | None:
        """
        Build a Qdrant filter from a dictionary.

        Args:
            filters: Dictionary of field: value pairs

        Returns:
            Qdrant Filter object or None
        """
        if not filters:
            return None

        conditions = []
        for key, value in filters.items():
            if isinstance(value, (str, int, float, bool)):
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )

        if not conditions:
            return None

        return Filter(must=conditions)

    def upsert(self, id: str, vector: list[float], metadata: dict[str]) -> None:
        """
        Insert or update a vector.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata
        """
        point_id = self._string_to_uuid(id)

        # Store original ID in metadata for retrieval
        payload = {**metadata, "_original_id": id}

        self._client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug(f"Upserted vector: {id}")

    def upsert_batch(self, items: list[tuple[str, list[float], dict[str]]]) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: List of (id, vector, metadata) tuples
        """
        if not items:
            return

        points = []
        for id, vector, metadata in items:
            point_id = self._string_to_uuid(id)
            payload = {**metadata, "_original_id": id}
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        # Batch upsert in chunks of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self._client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info(f"Batch upserted {len(items)} vectors")

    def similarity_search(
        self,
        vector: list[float],
        top_k: int = 10,
        filters: dict[str] | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve top-k most similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List of retrieval results with scores
        """
        qdrant_filter = self._build_filter(filters)

        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False,
        )

        retrieval_results: list[RetrievalResult] = []
        for result in results:
            payload = result.payload or {}
            original_id = payload.pop("_original_id", str(result.id))

            retrieval_results.append(
                RetrievalResult(
                    id=original_id,
                    score=result.score,
                    source="vector",
                    payload=payload,
                )
            )

        return retrieval_results

    def delete(self, id: str) -> bool:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete

        Returns:
            True if deleted, False if not found
        """
        point_id = self._string_to_uuid(id)

        try:
            # Check if exists first
            result = self._client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
            )

            if not result:
                return False

            self._client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=[point_id]),
            )
            logger.debug(f"Deleted vector: {id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting vector {id}: {e}")
            return False

    def delete_batch(self, ids: list[str]) -> int:
        """
        Delete multiple vectors by ID.

        Args:
            ids: List of vector identifiers to delete

        Returns:
            Number of vectors deleted
        """
        if not ids:
            return 0

        point_ids = [self._string_to_uuid(id) for id in ids]

        # Check which exist
        existing = self._client.retrieve(
            collection_name=self.collection_name,
            ids=point_ids,
        )
        existing_ids = [str(p.id) for p in existing]

        if not existing_ids:
            return 0

        self._client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=existing_ids),
        )

        deleted_count = len(existing_ids)
        logger.info(f"Batch deleted {deleted_count} vectors")
        return deleted_count

    def exists(self, id: str) -> bool:
        """
        Check if a vector exists.

        Args:
            id: Vector identifier

        Returns:
            True if exists, False otherwise
        """
        point_id = self._string_to_uuid(id)

        try:
            result = self._client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
            )
            return len(result) > 0

        except Exception:
            return False

    def get(self, id: str) -> tuple[list[float], dict[str]] | None:
        """
        Retrieve a vector and its metadata by ID.

        Args:
            id: Vector identifier

        Returns:
            Tuple of (vector, metadata) if found, None otherwise
        """
        point_id = self._string_to_uuid(id)

        try:
            result = self._client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_vectors=True,
                with_payload=True,
            )

            if not result:
                return None

            point = result[0]
            payload = dict(point.payload) if point.payload else {}
            payload.pop("_original_id", None)  # Remove internal field

            vector = point.vector if isinstance(point.vector, list) else list(point.vector)

            return (vector, payload)

        except Exception as e:
            logger.error(f"Error retrieving vector {id}: {e}")
            return None

    def clear(self) -> None:
        """Delete all vectors from the collection."""
        # Recreate the collection to clear all data
        self._client.delete_collection(collection_name=self.collection_name)
        self._ensure_collection()
        logger.info(f"Cleared collection: {self.collection_name}")

    def count(self) -> int:
        """
        Get total number of vectors.

        Returns:
            Vector count
        """
        collection_info = self._client.get_collection(collection_name=self.collection_name)
        return collection_info.points_count or 0

    def get_collection_info(self) -> dict[str]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection metadata
        """
        info = self._client.get_collection(collection_name=self.collection_name)
        return {
            "name": self.collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "status": str(info.status),
        }

    def search_with_score_threshold(
        self,
        vector: list[float],
        top_k: int = 10,
        score_threshold: float = 0.0,
        filters: dict[str] | None = None,
    ) -> list[RetrievalResult]:
        """
        Search with a minimum score threshold.

        Args:
            vector: Query vector
            top_k: Maximum number of results
            score_threshold: Minimum score to include in results
            filters: Optional metadata filters

        Returns:
            List of retrieval results above threshold
        """
        qdrant_filter = self._build_filter(filters)

        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=top_k,
            query_filter=qdrant_filter,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        retrieval_results: list[RetrievalResult] = []
        for result in results:
            payload = result.payload or {}
            original_id = payload.pop("_original_id", str(result.id))

            retrieval_results.append(
                RetrievalResult(
                    id=original_id,
                    score=result.score,
                    source="vector",
                    payload=payload,
                )
            )

        return retrieval_results
