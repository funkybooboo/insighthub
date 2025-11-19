"""
Embeddings Worker - Vector generation and Qdrant indexing.

Consumes: embeddings.generate
Produces: vector.index.updated
"""

import json
import logging
import os
import signal
import sys
from typing import Any

import pika
from shared.events import EmbeddingGenerateEvent, VectorIndexUpdatedEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))


class EmbeddingsWorker:
    """Embeddings generation worker."""

    def __init__(self):
        """Initialize the embeddings worker."""
        self.connection = None
        self.channel = None
        self.should_stop = False

    def connect(self):
        """Connect to RabbitMQ."""
        logger.info(f"Connecting to RabbitMQ: {RABBITMQ_URL}")
        self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True
        )

        # Declare queues
        self.channel.queue_declare(queue="embeddings.generate", durable=True)
        self.channel.queue_declare(queue="vector.index.updated", durable=True)

        # Bind queues
        self.channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE,
            queue="embeddings.generate",
            routing_key="embeddings.generate",
        )

        # Set QoS
        self.channel.basic_qos(prefetch_count=WORKER_CONCURRENCY)

        logger.info("Connected to RabbitMQ successfully")

    def on_embeddings_generate(self, ch, method, properties, body):
        """
        Handle embeddings.generate event.

        TODO: Implement embedding generation logic:
        1. Fetch chunks from PostgreSQL using event.chunk_ids
        2. Generate embeddings using Ollama/OpenAI
        3. Upsert vectors to Qdrant with metadata
        4. Publish vector.index.updated event
        """
        try:
            # Parse event
            event_data = json.loads(body)
            event = EmbeddingGenerateEvent(**event_data)

            logger.info(
                f"Generating embeddings for document {event.document_id}: "
                f"{len(event.chunk_ids)} chunks"
            )

            # TODO: Fetch chunks from database
            # chunks = db.query(Chunk).filter(Chunk.id.in_(event.chunk_ids)).all()

            # TODO: Generate embeddings
            # from shared.interfaces.vector import EmbeddingEncoder
            # embedder = OllamaEmbeddings(
            #     base_url=OLLAMA_BASE_URL,
            #     model=event.embedding_model
            # )
            # texts = [chunk.text for chunk in chunks]
            # vectors = embedder.encode(texts)

            # TODO: Upsert to Qdrant
            # from shared.interfaces.vector import VectorIndex
            # vector_store = QdrantVectorStore(url=QDRANT_URL)
            # for chunk, vector in zip(chunks, vectors):
            #     vector_store.upsert(
            #         id=chunk.id,
            #         vector=vector,
            #         metadata={
            #             "document_id": event.document_id,
            #             "workspace_id": event.workspace_id,
            #             "text": chunk.text,
            #             **chunk.metadata
            #         }
            #     )

            # Publish vector.index.updated event
            updated_event = VectorIndexUpdatedEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                chunk_count=len(event.chunk_ids),
                collection_name="documents",
                metadata=event.metadata,
            )
            self.publish_event("vector.index.updated", updated_event)

            logger.info(f"Successfully indexed {len(event.chunk_ids)} vectors")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def publish_event(self, routing_key: str, event: Any):
        """Publish an event to RabbitMQ."""
        event_dict = event.__dict__
        message = json.dumps(event_dict)

        self.channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(f"Published event: {routing_key}")

    def start(self):
        """Start consuming messages."""
        logger.info(f"Starting embeddings worker with concurrency {WORKER_CONCURRENCY}")

        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Connect
        self.connect()

        # Start consuming
        self.channel.basic_consume(
            queue="embeddings.generate",
            on_message_callback=self.on_embeddings_generate,
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
    worker = EmbeddingsWorker()
    worker.start()


if __name__ == "__main__":
    main()
