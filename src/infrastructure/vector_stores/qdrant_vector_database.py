"""Qdrant vector database implementation."""

import uuid
from typing import TYPE_CHECKING, Optional

from src.infrastructure.logger import create_logger
from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.retrieval import RetrievalResult

from .vector_database import VectorDatabase

if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Filter

logger = create_logger(__name__)


class VectorStoreException(Exception):
    """Exception raised when vector store operations fail."""

    def __init__(self, message: str, operation: str, original_error: Optional[Exception] = None):
        self.message = message
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Vector store operation '{operation}' failed: {message}")


try:
    import qdrant_client
    import qdrant_client.http.models as qdrant_models

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class QdrantVectorDatabase(VectorDatabase):
    """
    Qdrant implementation of VectorDatabase.

    Provides vector storage and similarity search using the Qdrant vector database.
    Supports filtering, batch operations, and metadata storage.

    Example:
        db = QdrantVectorDatabase(
            url="http://localhost:6333",
            collection_name="document",
            vector_size=384
        )
        db.upsert("chunk_1", [0.1, 0.2, ...], {"source": "doc.pdf"})
        results = db.similarity_search([0.1, 0.2, ...], top_k=5)
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "document",
        vector_size: int = 384,
        distance: str = "cosine",
        api_key: Optional[str] = None,
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
            "cosine": qdrant_models.Distance.COSINE,
            "euclidean": qdrant_models.Distance.EUCLID,
            "dot": qdrant_models.Distance.DOT,
        }
        self._distance = distance_map.get(distance.lower(), qdrant_models.Distance.COSINE)

        # Initialize client
        self._client: QdrantClient = qdrant_client.QdrantClient(url=url, api_key=api_key)

        # Ensure collection exists
        self._ensure_collection()

        logger.info(f"Connected to Qdrant at {url}, collection: {collection_name}")

    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.vector_size,
                        distance=self._distance,
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise VectorStoreException(
                str(e), operation="ensure_collection", original_error=e
            ) from e

    def _string_to_uuid(self, string_id: str) -> str:
        """
        Convert a string ID to a UUID format for Qdrant.

        Qdrant requires either UUID or integer IDs. We use UUID5 to create
        deterministic UUIDs from string IDs.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, string_id))

    def _build_filter(self, filters: Optional[FilterDict]) -> "Optional[Filter]":
        """
        Build a Qdrant filter from a dictionary.

        Args:
            filters: Dictionary of field: value pairs

        Returns:
            Qdrant Filter object or None
        """
        if not filters:
            return None

        # Create list with broader type to satisfy Filter.must
        conditions: list[
            qdrant_models.FieldCondition
            | qdrant_models.IsEmptyCondition
            | qdrant_models.IsNullCondition
            | qdrant_models.HasIdCondition
            | qdrant_models.HasVectorCondition
            | qdrant_models.NestedCondition
            | qdrant_models.Filter
        ] = []
        for key, value in filters.items():
            # Skip None and list values
            if value is None or isinstance(value, list):
                continue
            # MatchValue only accepts bool, int, str (not float)
            if isinstance(value, (str, int, bool)):
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                )
            elif isinstance(value, float):
                # Convert float to string for MatchValue
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=str(value)),
                    )
                )

        if not conditions:
            return None

        return qdrant_models.Filter(must=conditions)

    def upsert(self, id: str, vector: list[float], metadata: MetadataDict) -> None:
        """
        Insert or update a vector.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata

        Raises:
            VectorStoreException: If upsert fails
        """
        try:
            point_id = self._string_to_uuid(id)

            # Store original ID in metadata for retrieval
            payload = {**metadata, "_original_id": id}

            self._client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
            )
            logger.debug(f"Upserted vector: {id}")
        except Exception as e:
            logger.error(f"Failed to upsert vector {id}: {e}")
            raise VectorStoreException(str(e), operation="upsert", original_error=e) from e

    def upsert_batch(self, items: list[tuple[str, list[float], MetadataDict]]) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: List of (id, vector, metadata) tuples

        Raises:
            VectorStoreException: If batch upsert fails
        """
        if not items:
            return

        try:
            points = []
            for id, vector, metadata in items:
                point_id = self._string_to_uuid(id)
                payload = {**metadata, "_original_id": id}
                points.append(
                    qdrant_models.PointStruct(
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
        except Exception as e:
            logger.error(f"Failed to batch upsert {len(items)} vectors: {e}")
            raise VectorStoreException(str(e), operation="upsert_batch", original_error=e) from e

    def similarity_search(
        self,
        vector: list[float],
        top_k: int = 10,
        filters: Optional[FilterDict] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve top-k most similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List of retrieval results with scores

        Raises:
            VectorStoreException: If similarity search fails
        """
        try:
            qdrant_filter = self._build_filter(filters)

            results = self._client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=top_k,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=False,
            ).points

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
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise VectorStoreException(
                str(e), operation="similarity_search", original_error=e
            ) from e

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
                points_selector=qdrant_models.PointIdsList(points=[point_id]),
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

        from uuid import UUID

        point_ids = [self._string_to_uuid(id) for id in ids]

        # Check which exist
        existing = self._client.retrieve(
            collection_name=self.collection_name,
            ids=point_ids,
        )
        # Create list with broader type to satisfy PointIdsList
        existing_ids: list[int | str | UUID] = [str(p.id) for p in existing]

        if not existing_ids:
            return 0

        self._client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.PointIdsList(points=existing_ids),
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

    def get(self, id: str) -> Optional[tuple[list[float], MetadataDict]]:
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
            payload: MetadataDict = {}
            if point.payload:
                for key, val in point.payload.items():
                    if key != "_original_id" and isinstance(
                        val, (str, int, float, bool, type(None))
                    ):
                        payload[key] = val

            # Extract vector - only handle single list[float] case
            # Qdrant returns vectors as list[float] in most cases
            vector: list[float] = []
            if isinstance(point.vector, list) and point.vector:
                # Check if first element is a number (not a list)
                first_elem = point.vector[0]
                if isinstance(first_elem, (int, float)):
                    # It's list[float], rebuild it to satisfy type checker
                    vector = [
                        float(v) if isinstance(v, (int, float)) else 0.0 for v in point.vector
                    ]

            return (vector, payload)

        except Exception as e:
            logger.error(f"Error retrieving vector {id}: {e}")
            return None

    def clear(self) -> None:
        """Delete all vectors from the collection.

        Raises:
            VectorStoreException: If clearing collection fails
        """
        try:
            # Recreate the collection to clear all data
            self._client.delete_collection(collection_name=self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise VectorStoreException(str(e), operation="clear", original_error=e) from e

    def count(self) -> int:
        """
        Get total number of vectors.

        Returns:
            Vector count
        """
        collection_info = self._client.get_collection(collection_name=self.collection_name)
        return collection_info.points_count or 0

    def get_collection_info(self) -> dict[str, str | int]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection metadata
        """
        info = self._client.get_collection(collection_name=self.collection_name)
        return {
            "name": self.collection_name,
            "points_count": info.points_count or 0,
            "indexed_vectors_count": info.indexed_vectors_count or 0,
            "status": str(info.status),
        }

    def search_with_score_threshold(
        self,
        vector: list[float],
        top_k: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[FilterDict] = None,
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

        # Use query_points instead of search (modern qdrant-client API)
        results = self._client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k,
            query_filter=qdrant_filter,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        ).points

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
