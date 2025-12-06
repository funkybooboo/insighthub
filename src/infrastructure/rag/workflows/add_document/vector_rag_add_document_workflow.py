"""Vector RAG add document workflow implementation.

This workflow orchestrates the full Vector RAG document ingestion process:
1. Parse document from binary
2. Chunk document into segments
3. Embed chunks into vectors
4. Index vectors in vector store
"""

from typing import BinaryIO, Optional

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.rag.steps.general.parsing.document_parser import DocumentParser
from src.infrastructure.rag.steps.vector_rag.embedding.vector_embedder import VectorEmbeddingEncoder
from src.infrastructure.rag.workflows.add_document.add_document_workflow import (
    AddDocumentWorkflow,
    AddDocumentWorkflowError,
)
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.vector_stores import VectorStore

logger = create_logger(__name__)


class VectorRagAddDocumentWorkflow(AddDocumentWorkflow):
    """
    Orchestrates document consumption: parse -> chunk -> embed -> index.

    This workflow encapsulates the complete RAG ingestion pipeline.
    Workers execute this workflow in background threads.
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        embedder: VectorEmbeddingEncoder,
        vector_store: VectorStore,
    ) -> None:
        """
        Initialize the consume workflow.

        Args:
            parser: Document parser implementation
            chunker: Document chunker implementation
            embedder: Vector embedding encoder
            vector_store: Vector store for indexing
        """
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def execute(
        self,
        raw_document: BinaryIO,
        document_id: str,
        workspace_id: str,
        metadata: Optional[MetadataDict] = None,
    ) -> Result[int, AddDocumentWorkflowError]:
        """
        Execute the full consume workflow.

        Args:
            raw_document: Binary document content
            document_id: Unique document identifier
            workspace_id: Workspace identifier
            metadata: Optional metadata to attach

        Returns:
            Result containing number of chunks indexed, or error
        """
        # Step 1: Parse document
        logger.info(f"[ConsumeWorkflow] Parsing document {document_id}")
        parse_result = self.parser.parse(raw_document, metadata)

        if isinstance(parse_result, Failure):
            return Failure(
                AddDocumentWorkflowError(
                    f"Failed to parse document: {parse_result.failure()}",
                    step="parse",
                )
            )

        document = parse_result.unwrap()
        logger.info(
            f"[ConsumeWorkflow] Parsed document {document_id}: {len(document.content)} chars"
        )

        # Step 2: Chunk document
        logger.info(f"[ConsumeWorkflow] Chunking document {document_id}")
        try:
            chunks = self.chunker.chunk(document)
            logger.info(
                f"[ConsumeWorkflow] Created {len(chunks)} chunks for document {document_id}"
            )
        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    f"Failed to chunk document: {e}",
                    step="chunk",
                )
            )

        if not chunks:
            logger.warning(f"[ConsumeWorkflow] No chunks created for document {document_id}")
            return Success(0)

        # Step 3: Embed chunks
        logger.info(f"[ConsumeWorkflow] Embedding {len(chunks)} chunks")
        embed_result = self._embed_chunks(chunks)
        if isinstance(embed_result, Failure):
            return embed_result
        embeddings = embed_result.unwrap()

        # Step 4: Index in vector store
        logger.info(f"[ConsumeWorkflow] Indexing {len(chunks)} chunks in vector store")
        try:
            chunk_ids = [chunk.id for chunk in chunks]
            payloads = [
                {
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "chunk_id": chunk.id,
                    "text": chunk.text,
                    **(chunk.metadata or {}),
                }
                for chunk in chunks
            ]

            self.vector_store.add(
                vectors=embeddings,
                ids=chunk_ids,
                payloads=payloads,
            )

            logger.info(
                f"[ConsumeWorkflow] Successfully indexed {len(chunks)} chunks for document {document_id}"
            )
            return Success(len(chunks))

        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    f"Failed to index chunks: {e}",
                    step="index",
                )
            )

    def _embed_chunks(self, chunks: list) -> Result[list, AddDocumentWorkflowError]:
        """Embed chunks and return embeddings or error."""
        try:
            chunk_texts = [chunk.text for chunk in chunks]
            result = self.embedder.encode(chunk_texts)

            if isinstance(result, Failure):
                error = result.failure()
                return Failure(
                    AddDocumentWorkflowError(
                        f"Failed to embed chunks: {error.message}",
                        step="embed",
                    )
                )

            embeddings = result.unwrap()
            logger.info(f"[ConsumeWorkflow] Generated {len(embeddings)} embeddings")
            return Success(embeddings)

        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    f"Failed to embed chunks: {e}",
                    step="embed",
                )
            )
