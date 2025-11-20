"""
Example: How to use StatusService in a worker.

This shows the complete pattern for updating document status during processing.
"""

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.messaging.publisher import RabbitMQPublisher
from shared.repositories.status import SqlStatusRepository
from shared.services.status_service import StatusService
from shared.types.status import DocumentProcessingStatus

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Example document processor using StatusService."""

    def __init__(self):
        """Initialize the processor with all dependencies."""
        # Database setup
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable required")
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()

        # RabbitMQ publisher setup (optional - graceful degradation)
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        publisher = None
        if rabbitmq_url:
            exchange = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
            publisher = RabbitMQPublisher(rabbitmq_url=rabbitmq_url, exchange=exchange)
            logger.info("RabbitMQ publisher initialized for status updates")
        else:
            logger.warning("RABBITMQ_URL not set - status updates will not be broadcast")

        # Create StatusService with dependency injection
        status_repository = SqlStatusRepository(self.db)
        self.status_service = StatusService(
            status_repository=status_repository,
            message_publisher=publisher
        )
        
        logger.info("DocumentProcessor initialized with StatusService")

    def process_document(self, document_id: int, file_path: str) -> None:
        """
        Process a document through the full pipeline with status updates.

        Args:
            document_id: Document ID to process
            file_path: Path to document file
        """
        logger.info(f"Processing document {document_id} from {file_path}")

        # Step 1: Mark as processing
        result = self.status_service.update_document_status(
            document_id=document_id,
            status=DocumentProcessingStatus.PROCESSING
        )

        if result.is_err():
            logger.error(f"Failed to update document status: {result.error}")
            return

        try:
            # Step 2: Parse document
            logger.info(f"Parsing document {document_id}...")
            text = self._parse_document(file_path)
            
            # Step 3: Chunk text
            logger.info(f"Chunking document {document_id}...")
            chunks = self._chunk_text(text)
            
            # Step 4: Generate embeddings
            logger.info(f"Generating embeddings for document {document_id}...")
            embeddings = self._generate_embeddings(chunks)
            
            # Step 5: Index to vector store
            logger.info(f"Indexing document {document_id} to vector store...")
            self._index_to_vector_store(document_id, chunks, embeddings)
            
            # Step 6: Mark as ready
            result = self.status_service.update_document_status(
                document_id=document_id,
                status=DocumentProcessingStatus.READY,
                chunk_count=len(chunks),
                metadata={
                    "embedding_model": "nomic-embed-text",
                    "chunk_strategy": "sentence",
                    "vector_store": "qdrant"
                }
            )

            if result.is_ok():
                logger.info(f"Document {document_id} processed successfully - {len(chunks)} chunks")
            else:
                logger.error(f"Failed to mark document as ready: {result.error}")

        except Exception as e:
            # Step 7: Mark as failed on error
            logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
            
            result = self.status_service.update_document_status(
                document_id=document_id,
                status=DocumentProcessingStatus.FAILED,
                error=str(e)
            )

            if result.is_err():
                logger.error(f"Failed to mark document as failed: {result.error}")

    def _parse_document(self, file_path: str) -> str:
        """Parse document and extract text (implementation depends on file type)."""
        # TODO: Implement actual parsing logic
        return "Sample document text"

    def _chunk_text(self, text: str) -> list[str]:
        """Chunk text into smaller pieces (implementation depends on strategy)."""
        # TODO: Implement actual chunking logic
        return [text[i:i+1000] for i in range(0, len(text), 1000)]

    def _generate_embeddings(self, chunks: list[str]) -> list[list[float]]:
        """Generate embeddings for chunks (implementation depends on model)."""
        # TODO: Implement actual embedding generation
        return [[0.1] * 768 for _ in chunks]

    def _index_to_vector_store(
        self, 
        document_id: int, 
        chunks: list[str], 
        embeddings: list[list[float]]
    ) -> None:
        """Index chunks and embeddings to vector store."""
        # TODO: Implement actual vector store indexing
        pass


# Example usage in main worker loop
def main():
    """Main worker loop example."""
    processor = DocumentProcessor()
    
    # In your actual RabbitMQ consumer callback:
    def on_document_uploaded(event: dict):
        document_id = event["document_id"]
        file_path = event["file_path"]
        
        try:
            processor.process_document(document_id, file_path)
        except Exception as e:
            logger.error(f"Unhandled error processing document {document_id}: {e}")

    # Your RabbitMQ consumer setup here...
    logger.info("Worker started, waiting for documents...")


if __name__ == "__main__":
    main()
