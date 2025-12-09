"""Qdrant implementation of VectorStore interface."""

import uuid
from typing import TYPE_CHECKING, List, Optional, Tuple

from src.infrastructure.logger import create_logger
from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.document import Chunk

from .vector_store import VectorStore, VectorStoreException

if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Filter

logger = create_logger(__name__)


try:
    import qdrant_client
    import qdrant_client.http.models as qdrant_models

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class QdrantVectorStore(VectorStore):
    """
    Qdrant implementation of VectorStore.

    Provides vector storage and similarity search using the Qdrant vector database.
    Supports filtering, batch operations, and metadata storage.

    Example:
        store = QdrantVectorStore(
            url="http://localhost:6333",
            collection_name="document",
            vector_size=384
        )
        store.add(vectors, ids, payloads)
        results = store.search(query_embedding, top_k=5)
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
        Initialize Qdrant vector store.

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

    def add(self, vectors: List[List[float]], ids: List[str], payloads: List[MetadataDict]) -> None:
        """
        Add vectors to the vector store.

        Args:
            vectors: List of vector embeddings
            ids: List of unique IDs for the vectors
            payloads: List of metadata payloads for the vectors

        Raises:
            VectorStoreException: If adding vectors fails
        """
        if not vectors:
            logger.warning("No vectors to add")
            return

        # Validate input lengths match
        if len(vectors) != len(ids) or len(vectors) != len(payloads):
            raise ValueError(
                f"Input lengths don't match: vectors={len(vectors)}, ids={len(ids)}, payloads={len(payloads)}"
            )

        try:
            points = []
            for id_, vector, payload in zip(ids, vectors, payloads):
                point_id = self._string_to_uuid(id_)
                # Store original ID in metadata for retrieval
                payload_with_id = {**payload, "_original_id": id_}
                points.append(
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload_with_id,
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

            logger.info(f"Added {len(vectors)} vectors to vector store")
        except Exception as e:
            logger.error(f"Failed to add {len(vectors)} vectors: {e}")
            raise VectorStoreException(str(e), operation="add", original_error=e) from e

    def search(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[FilterDict] = None
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks in the vector store.

        Args:
            query_embedding: The embedding of the query
            top_k: The number of similar chunks to return
            filters: Optional metadata filters

        Returns:
            A list of tuples, where each tuple contains a chunk and its similarity score

        Raises:
            VectorStoreException: If searching fails
        """
        try:
            qdrant_filter = self._build_filter(filters)

            results = self._client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=False,
            ).points

            # Convert results to (Chunk, score) tuples
            chunk_results: List[Tuple[Chunk, float]] = []
            for result in results:
                payload = result.payload or {}
                original_id = payload.pop("_original_id", str(result.id))

                # Extract chunk data from metadata
                document_id = str(payload.get("document_id", ""))
                text = str(payload.get("text", ""))

                # Remove our internal fields to get original metadata
                original_metadata = {
                    k: v
                    for k, v in payload.items()
                    if k
                    not in (
                        "document_id",
                        "text",
                        "workspace_id",
                        "chunk_id",
                        "chunk_index",
                        "start_offset",
                        "end_offset",
                        "sentence_count",
                    )
                }

                # Reconstruct chunk
                chunk = Chunk(
                    id=original_id,
                    document_id=document_id,
                    text=text,
                    metadata=original_metadata,  # type: ignore  # Metadata types are flexible
                )

                chunk_results.append((chunk, result.score))

            logger.info(f"Found {len(chunk_results)} similar chunks")
            return chunk_results
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise VectorStoreException(str(e), operation="search", original_error=e) from e

    def clear(self) -> None:
        """
        Clear all vectors from the collection.

        This recreates the collection, effectively deleting all stored vectors.

        Raises:
            VectorStoreException: If clearing fails
        """
        logger.warning(f"Clearing all vectors from collection: {self.collection_name}")

        try:
            # Recreate the collection to clear all data
            self._client.delete_collection(collection_name=self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise VectorStoreException(str(e), operation="clear", original_error=e) from e

    def delete(self, filters: FilterDict) -> int:
        """
        Delete vectors from the vector store based on metadata filters.

        Args:
            filters: A dictionary of metadata key-value pairs to match.

        Returns:
            The number of vectors deleted.

        Raises:
            VectorStoreException: If deleting vectors fails.
        """
        logger.info(f"Deleting vectors with filter: {filters}")

        if not QDRANT_AVAILABLE:
            return 0

        qdrant_filter = self._build_filter(filters)
        if not qdrant_filter:
            return 0

        try:
            # Scroll through all points matching the filter to get their IDs
            point_ids = []
            offset = None
            while True:
                scroll_result, next_offset = self._client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=qdrant_filter,
                    limit=256,  # Batch size
                    offset=offset,
                    with_payload=False,
                    with_vectors=False,
                )
                if not scroll_result:
                    break

                point_ids.extend([point.id for point in scroll_result])

                if next_offset is None:
                    break
                offset = next_offset

            if not point_ids:
                return 0

            # Delete the collected point IDs in batches
            self._client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_models.PointIdsList(points=point_ids),
            )

            deleted_count = len(point_ids)
            logger.info(f"Deleted {deleted_count} points matching filter.")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete by filter: {e}")
            raise VectorStoreException(str(e), operation="delete", original_error=e) from e
