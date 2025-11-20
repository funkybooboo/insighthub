"""
Ingestion Worker - Document parsing and chunking.

Consumes: document.uploaded
Produces: document.chunks.ready, embeddings.generate, document.graph.build
"""

import json
import logging
import os
import signal
import sys
from typing import Any

import pika
from shared.database.session import create_session
from shared.events import (
    DocumentChunksReadyEvent,
    DocumentGraphBuildEvent,
    DocumentUploadedEvent,
    EmbeddingGenerateEvent,
)
from shared.messaging.publisher import RabbitMQPublisher
from shared.repositories.status import SqlStatusRepository
from shared.services.status_service import StatusService
from shared.types.status import DocumentProcessingStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
WORKER_NAME = os.getenv("WORKER_NAME", "ingestion")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))


class IngestionWorker:
    """Document ingestion worker."""

    def __init__(self):
        """Initialize the ingestion worker."""
        self.connection = None
        self.channel = None
        self.should_stop = False
        self.status_service: StatusService | None = None
        self.db_session = None

    def connect(self):
        """Connect to RabbitMQ and initialize services."""
        logger.info(f"Connecting to RabbitMQ: {RABBITMQ_URL}")
        self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True
        )

        # Declare queues
        self.channel.queue_declare(queue="document.uploaded", durable=True)
        self.channel.queue_declare(queue="document.chunks.ready", durable=True)
        self.channel.queue_declare(queue="embeddings.generate", durable=True)
        self.channel.queue_declare(queue="document.graph.build", durable=True)

        # Bind queues to exchange
        self.channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE, queue="document.uploaded", routing_key="document.uploaded"
        )

        # Set QoS to process one message at a time
        self.channel.basic_qos(prefetch_count=WORKER_CONCURRENCY)

        # Initialize database session
        self.db_session = next(create_session())
        
        # Initialize status service with publisher
        publisher = RabbitMQPublisher(
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE
        )
        publisher.connect()
        
        status_repository = SqlStatusRepository(self.db_session)
        self.status_service = StatusService(
            status_repository=status_repository,
            message_publisher=publisher
        )

        logger.info("Connected to RabbitMQ and initialized status service successfully")

    def on_document_uploaded(self, ch, method, properties, body):
        """
        Handle document.uploaded event.

        TODO: Implement document ingestion using shared orchestrators:
        
        # 1. Initialize dependencies
        # parser = PDFParser() or TextParser() depending on mime_type
        # chunker = SentenceChunker(chunk_size=500)
        # enricher = DefaultEnricher()
        # embedder = OllamaEmbeddings(...)
        # vector_index = QdrantVectorStore(...)
        
        # 2. Use VectorRAGIndexer
        # from shared.orchestrators.vector_rag import VectorRAGIndexer
        # indexer = VectorRAGIndexer(parser, chunker, enricher, embedder, vector_index)
        # indexer.ingest([(document_bytes, event.metadata)])
        
        # 3. Publish events for next stages (Graph, etc.)
        """
        try:
            # Parse event
            event_data = json.loads(body)
            event = DocumentUploadedEvent(**event_data)

            logger.info(f"Processing document: {event.document_id} - {event.filename}")

            # TODO: Download document from MinIO
            # from minio import Minio
            # minio_client = Minio(...)
            # document_bytes = minio_client.get_object(bucket, event.storage_path)

            # TODO: Parse document based on file type
            # if event.filename.endswith('.pdf'):
            #     from shared.interfaces.vector import DocumentParser
            #     parser = PDFParser()
            #     document = parser.parse(document_bytes, metadata=event.metadata)
            # elif event.filename.endswith('.txt'):
            #     document = TextParser().parse(document_bytes, metadata=event.metadata)

            # TODO: Chunk document
            # from shared.interfaces.vector import Chunker
            # chunker = SentenceChunker(chunk_size=500, overlap=50)
            # chunks = chunker.chunk(document)

            # TODO: Store chunks in PostgreSQL
            # for chunk in chunks:
            #     db.add(ChunkModel(
            #         id=chunk.id,
            #         document_id=event.document_id,
            #         text=chunk.text,
            #         metadata=chunk.metadata
            #     ))
            # db.commit()

            # TODO: Get chunk IDs
            chunk_ids = []  # Replace with actual chunk IDs

            # Publish document.chunks.ready event
            chunks_ready_event = DocumentChunksReadyEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                chunk_ids=chunk_ids,
                chunk_count=len(chunk_ids),
                metadata=event.metadata,
            )
            self.publish_event("document.chunks.ready", chunks_ready_event)

            # Publish embeddings.generate event
            embeddings_event = EmbeddingGenerateEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                chunk_ids=chunk_ids,
                embedding_model="nomic-embed-text",
                metadata=event.metadata,
            )
            self.publish_event("embeddings.generate", embeddings_event)

            # Publish document.graph.build event
            graph_event = DocumentGraphBuildEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                chunk_ids=chunk_ids,
                metadata=event.metadata,
            )
            self.publish_event("document.graph.build", graph_event)

            logger.info(
                f"Successfully processed document {event.document_id}: {len(chunk_ids)} chunks"
            )

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def publish_event(self, routing_key: str, event: Any):
        """Publish an event to RabbitMQ."""
        # Convert dataclass to dict
        event_dict = event.__dict__
        message = json.dumps(event_dict)

        self.channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent
        )
        logger.info(f"Published event: {routing_key}")

    def start(self):
        """Start consuming messages."""
        logger.info(f"Starting {WORKER_NAME} worker with concurrency {WORKER_CONCURRENCY}")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Connect to RabbitMQ
        self.connect()

        # Start consuming
        self.channel.basic_consume(
            queue="document.uploaded",
            on_message_callback=self.on_document_uploaded,
            auto_ack=False,
        )

        logger.info("Waiting for messages. To exit press CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the worker gracefully."""
        logger.info("Stopping worker...")
        self.should_stop = True
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
        if self.connection and self.connection.is_open:
            self.connection.close()
        logger.info("Worker stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    worker = IngestionWorker()
    worker.start()


if __name__ == "__main__":
    main()
