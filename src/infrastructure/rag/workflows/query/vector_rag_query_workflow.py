"""Vector RAG query workflow implementation.

This workflow orchestrates the full Vector RAG query process:
1. Embed query text
2. Search vector store
3. Rerank results (optional)
4. Return context
"""

from typing import Optional

from returns.result import Failure

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.vector_rag.embedding.vector_embedder import VectorEmbeddingEncoder
from src.infrastructure.rag.steps.vector_rag.reranking.reranker import Reranker
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow, QueryWorkflowError
from src.infrastructure.types.common import FilterDict
from src.infrastructure.types.document import Chunk
from src.infrastructure.types.rag import ChunkData
from src.infrastructure.vector_stores import VectorStore

logger = create_logger(__name__)


class VectorRagQueryWorkflow(QueryWorkflow):
    """
    Orchestrates query processing: embed -> search -> rerank.

    This workflow encapsulates the complete RAG retrieval pipeline.
    Workers execute this workflow in background threads.
    """

    def __init__(
        self,
        embedder: VectorEmbeddingEncoder,
        vector_store: VectorStore,
        reranker: Optional[Reranker] = None,
    ) -> None:
        """
        Initialize the query workflow.

        Args:
            embedder: Vector embedding encoder
            vector_store: Vector store for search
            reranker: Optional reranker for result refinement
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker

    def execute(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[FilterDict] = None,
    ) -> list[ChunkData]:
        """
        Execute the full query workflow.

        Args:
            query_text: User's query text
            top_k: Number of results to return
            filters: Optional filters for vector search

        Returns:
            List of relevant chunks with scores

        Raises:
            QueryWorkflowError: If any step fails
        """
        # Step 1: Embed query
        logger.info(f"[QueryWorkflow] Embedding query: {query_text[:50]}...")
        try:
            result = self.embedder.encode([query_text])
            if isinstance(result, Failure):
                error = result.failure()
                raise QueryWorkflowError(f"Failed to embed query: {error.message}", step="embed")
            query_embeddings = result.unwrap()
            if not query_embeddings:
                raise QueryWorkflowError("Embedder returned empty results", step="embed")
            query_vector = query_embeddings[0]
            logger.info(f"[QueryWorkflow] Generated query embedding (dim={len(query_vector)})")
        except QueryWorkflowError:
            raise
        except Exception as e:
            raise QueryWorkflowError(f"Failed to embed query: {e}", step="embed") from e

        # Step 2: Search vector store
        logger.info(f"[QueryWorkflow] Searching vector store (top_k={top_k}, filters={filters})")
        try:
            # Adjust top_k for reranking if reranker is present
            search_k = top_k * 3 if self.reranker else top_k

            results = self.vector_store.search(
                query_embedding=query_vector,
                top_k=search_k,
                filters=filters,
            )
            logger.info(f"[QueryWorkflow] Found {len(results)} results from vector store")
        except Exception as e:
            raise QueryWorkflowError(f"Failed to search vector store: {e}", step="search") from e

        # Step 3: Rerank results (if reranker provided)
        if self.reranker and results:
            results = self._apply_reranking(query_text, results, top_k)
        else:
            results = results[:top_k]

        # Step 4: Convert to ChunkData
        chunk_data: list[ChunkData] = []
        for chunk, score in results:
            chunk_data.append(
                ChunkData(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=score,
                    metadata=chunk.metadata or {},
                )
            )

        logger.info(f"[QueryWorkflow] Returning {len(chunk_data)} chunks for query")
        return chunk_data

    def _apply_reranking(
        self, query_text: str, results: list[tuple[Chunk, float]], top_k: int
    ) -> list[tuple[Chunk, float]]:
        """Apply reranking to search results and return top_k reranked results."""
        logger.info(f"[QueryWorkflow] Reranking {len(results)} results")

        try:
            reranked = self._rerank_results(query_text, results)
            if reranked is None:
                return results[:top_k]
            return reranked[:top_k]
        except Exception as e:
            logger.warning(f"[QueryWorkflow] Reranking failed, using original results: {e}")
            return results[:top_k]

    def _rerank_results(
        self, query_text: str, results: list[tuple[Chunk, float]]
    ) -> Optional[list[tuple[Chunk, float]]]:
        """Rerank results using the reranker, return None on failure."""
        if not self.reranker:
            return None

        texts = [chunk.text for chunk, _ in results]
        scores = [score for _, score in results]
        rerank_result = self.reranker.rerank(query=query_text, texts=texts, scores=scores)

        if isinstance(rerank_result, Failure):
            logger.warning(f"[QueryWorkflow] Reranking failed: {rerank_result.failure()}")
            return None

        reranked_pairs = rerank_result.unwrap()
        text_to_chunk = {chunk.text: chunk for chunk, _ in results}
        mapped_results = [
            (text_to_chunk[text], score) for text, score in reranked_pairs if text in text_to_chunk
        ]

        logger.info(f"[QueryWorkflow] Reranked to {len(mapped_results)} results")
        return mapped_results
