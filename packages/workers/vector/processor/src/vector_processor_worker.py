"""Vector processor worker - consolidated embedding generation and vector indexing."""

import logging
from typing import Any, Dict

from shared.config import Config
from shared.database.vector import create_vector_store, VectorStore
from shared.documents.embedding import VectorEmbeddingEncoder, create_embedding_encoder
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.models.chunk import Chunk as DbChunk
from shared.repositories.chunk import SqlChunkRepository
from shared.types.document import Chunk as TypeChunk
from shared.worker import Worker

logger = logging.getLogger(__name__)


class VectorProcessorWorker(Worker):
    """Consolidated worker for vector processing: embedding generation and vector indexing."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: Config,
        chunk_repository: SqlChunkRepository,
        embedding_encoder: VectorEmbeddingEncoder,
        vector_store: VectorStore,
    ):
        """Initialize the vector processor worker."""
        super().__init__(consumer, publisher, config)
        self.chunk_repo = chunk_repository
        self.embedding_encoder = embedding_encoder
        self.vector_store = vector_store

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process vector processing message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.chunked":
                self._process_document_chunks(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing vector processing message: {e}")

    def _process_document_chunks(self, message: Dict[str, Any]) -> None:
        """Process document chunks through embedding and indexing."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # Get chunks from chunk repository
            chunks = self.chunk_repo.get_by_document(int(document_id))

            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return

            logger.info(f"Processing {len(chunks)} chunks for document {document_id}")

            # Step 1: Generate embeddings for all chunks
            chunk_texts = [chunk.chunk_text for chunk in chunks]
            embeddings_result = self.embedding_encoder.encode(chunk_texts)

            if embeddings_result.is_err():
                logger.error(f"Failed to generate embeddings: {embeddings_result.err()}")
                return

            embeddings = embeddings_result.ok()

            # Step 2: Update chunks with embeddings and convert to types for vector store
            type_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding

                # Convert database chunk to type chunk for vector store
                type_chunk = TypeChunk(
                    id=chunk.chunk_id,  # Use chunk_id as unique identifier
                    document_id=str(chunk.document_id),
                    text=chunk.chunk_text,
                    metadata=chunk.metadata,
                    vector=embedding,
                )
                type_chunks.append(type_chunk)

            # Step 3: Index chunks in vector store
            self.vector_store.add(type_chunks)

            # Step 4: Update chunks in database with embeddings
            for chunk in chunks:
                self.chunk_repo.update_embedding(chunk.id, chunk.embedding)  # type: ignore  # chunk.id exists from DB

            # Publish completion event
            self.publisher.publish_event(
                event_type="document.indexed",
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_count=len(chunks),
                indexed_count=len(chunks),
            )

            logger.info(
                f"Completed vector processing for document {document_id}: "
                f"{len(chunks)} chunks processed and indexed"
            )

        except Exception as e:
            logger.error(f"Error in vector processing pipeline for document {document_id}: {e}")
            # Publish error event
            self.publisher.publish_event(
                event_type="document.indexing_failed",
                document_id=document_id,
                workspace_id=workspace_id,
                error=str(e),
            )


def create_vector_processor_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: Config,
) -> VectorProcessorWorker:
    """Create a vector processor worker with all dependencies."""
    from shared.database.sql.postgres import PostgresConnection
    from shared.repositories.chunk.factory import create_chunk_repository

    # Create database connection
    db_conn = PostgresConnection(
        host=config.database_host,
        port=config.database_port,
        database=config.database_name,
        user=config.database_user,
        password=config.database_password,
    )

    # Create chunk repository
    chunk_repository = create_chunk_repository(db_conn)

    # Create embedding encoder
    embedding_encoder = create_embedding_encoder(
        provider=config.embedding_provider or "ollama",
        model_name=config.embedding_model or "nomic-embed-text",
        base_url=config.ollama_base_url,
    )

    # Create vector store
    vector_store = create_vector_store(
        db_type="qdrant",
        url=config.qdrant_url or "http://localhost:6333",
        collection_name=config.qdrant_collection or "documents",
        vector_size=config.embedding_dimension or 768,
    )

    if not vector_store:
        raise RuntimeError("Failed to create vector store")

    return VectorProcessorWorker(
        consumer=consumer,
        publisher=publisher,
        config=config,
        chunk_repository=chunk_repository,  # type: ignore  # create_chunk_repository returns correct type
        embedding_encoder=embedding_encoder,
        vector_store=vector_store,
    )
