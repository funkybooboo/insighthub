"""
Chucker Worker - Document chunking for embeddings.

Consumes: document.parsed
Produces: document.chunked
"""

import uuid
from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.workers import BaseWorker
from shared.logger import create_logger

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
WORKER_CONCURRENCY = config.worker_concurrency
CHUNK_SIZE = config.chunk_size
CHUNK_OVERLAP = config.chunk_overlap
CHUNK_STRATEGY = "character"  # Could be added to config if needed


@dataclass
class DocumentChunkedEvent:
    """Event emitted when document is chunked."""

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    chunk_count: int
    metadata: dict[str, Any]


class TextChunker:
    """Text chunking utility for different strategies."""

    def __init__(self, chunk_size: int, chunk_overlap: int, strategy: str):
        """Initialize the text chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

        # TODO: Initialize NLTK if using sentence strategy
        # if strategy == "sentence":
        #     import nltk
        #     # Download punkt tokenizer if needed

    def chunk_text(self, text: str) -> list[str]:
        """
        Chunk text based on the configured strategy.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        # TODO: Implement different chunking strategies
        # 1. Character-based chunking
        # 2. Word-based chunking
        # 3. Sentence-based chunking with NLTK

        # Placeholder: simple character-based chunking
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= text_length:
                break

        return chunks


class ChuckerWorker(BaseWorker):
    """Document chunker worker."""

    def __init__(self) -> None:
        """Initialize the chucker worker."""
        super().__init__(
            worker_name="chucker",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.parsed",
            consume_queue="chucker.document.parsed",
            prefetch_count=WORKER_CONCURRENCY,
        )

        # Initialize text chunker
        self.chunker = TextChunker(CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_STRATEGY)

    def process_event(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Process document.parsed event to create chunks.

        Args:
            event_data: Event data containing document_id, workspace_id, etc.
            message_context: Message context information
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Chunking document",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "chunk_size": self.chunker.chunk_size,
                "strategy": self.chunker.strategy
            }
        )

        try:
            # TODO: Get parsed text from database
            text_content = self._get_parsed_text(document_id)
            if not text_content:
                raise ValueError(f"No parsed text found for document {document_id}")

            # Chunk the text
            text_chunks = self.chunker.chunk_text(text_content)

            # TODO: Store chunks in database
            chunk_ids = self._store_chunks(document_id, text_chunks)

            # TODO: Update document status
            self._update_document_status(document_id, "chunked", {
                "chunk_count": len(chunk_ids),
                "total_chunks": len(text_chunks)
            })

            # Publish document.chunked event
            chunked_event = DocumentChunkedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_ids=chunk_ids,
                chunk_count=len(chunk_ids),
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.chunked",
                event_data=asdict(chunked_event),
                correlation_id=message_context.get("correlation_id"),
                message_id=document_id,
            )

            logger.info(
                "Successfully chunked document",
                extra={
                    "document_id": document_id,
                    "chunk_count": len(chunk_ids)
                }
            )

        except Exception as e:
            logger.error(
                "Failed to chunk document",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            # TODO: Update document status to failed
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _get_parsed_text(self, document_id: str) -> str | None:
        """Get parsed text from database."""
        # TODO: Implement database query
        # 1. Connect to PostgreSQL
        # 2. Query documents table for parsed_text
        # 3. Handle connection errors
        return f"Mock parsed text for document {document_id}"

    def _store_chunks(self, document_id: str, chunks: list[str]) -> list[str]:
        """Store text chunks in database and return chunk IDs."""
        # TODO: Implement chunk storage
        # 1. Connect to PostgreSQL
        # 2. Insert chunks into document_chunks table
        # 3. Generate UUIDs for chunk IDs
        # 4. Handle transaction and errors

        chunk_ids = []
        for i, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)
            # TODO: Insert into database

        return chunk_ids

    def _update_document_status(self, document_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        """Update document processing status."""
        # TODO: Implement status update
        # 1. Connect to PostgreSQL
        # 2. Update processing_status and processing_metadata
        # 3. Handle connection errors
        pass


def main() -> None:
    """Main entry point."""
    worker = ChuckerWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping chucker worker")
        worker.stop()


if __name__ == "__main__":
    main()