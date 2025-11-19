"""
Graph Worker - Entity extraction and graph construction.

Consumes: document.graph.build
Produces: graph.build.complete
"""

import json
import logging
import os
import signal
import sys
from typing import Any

import pika
from shared.events import DocumentGraphBuildEvent, GraphBuildCompleteEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))


class GraphWorker:
    """Graph building worker."""

    def __init__(self):
        """Initialize the graph worker."""
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
        self.channel.queue_declare(queue="document.graph.build", durable=True)
        self.channel.queue_declare(queue="graph.build.complete", durable=True)

        # Bind queues
        self.channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE,
            queue="document.graph.build",
            routing_key="document.graph.build",
        )

        # Set QoS
        self.channel.basic_qos(prefetch_count=WORKER_CONCURRENCY)

        logger.info("Connected to RabbitMQ successfully")

    def on_graph_build(self, ch, method, properties, body):
        """
        Handle document.graph.build event.

        TODO: Implement graph building logic:
        1. Fetch chunks from PostgreSQL
        2. Extract entities using LLM/NER
        3. Extract relations between entities
        4. Build knowledge graph
        5. Apply Leiden clustering
        6. Store in graph database (PostgreSQL/Neo4j)
        7. Publish graph.build.complete event
        """
        try:
            # Parse event
            event_data = json.loads(body)
            event = DocumentGraphBuildEvent(**event_data)

            logger.info(
                f"Building graph for document {event.document_id}: "
                f"{len(event.chunk_ids)} chunks"
            )

            # TODO: Fetch chunks
            # chunks = db.query(Chunk).filter(Chunk.id.in_(event.chunk_ids)).all()

            # TODO: Extract entities
            # from shared.interfaces.graph import EntityExtractor
            # entity_extractor = LLMEntityExtractor(llm)
            # entities = entity_extractor.extract_entities_batch(chunks)

            # TODO: Extract relations
            # from shared.interfaces.graph import RelationExtractor
            # relation_extractor = LLMRelationExtractor(llm)
            # relations = relation_extractor.extract_relations_batch(chunks, entities)

            # TODO: Build graph
            # from shared.interfaces.graph import GraphBuilder
            # graph_builder = LeidenGraphBuilder()
            # nodes, edges = graph_builder.build_graph(documents)
            # clustering = graph_builder.apply_clustering(nodes, edges)

            # TODO: Store in graph database
            # graph_store = Neo4jGraphStore(uri=...)
            # graph_store.add_nodes(nodes)
            # graph_store.add_edges(edges)

            # Placeholder values
            node_count = 0
            edge_count = 0
            community_count = 0

            # Publish graph.build.complete event
            complete_event = GraphBuildCompleteEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                node_count=node_count,
                edge_count=edge_count,
                community_count=community_count,
                metadata=event.metadata,
            )
            self.publish_event("graph.build.complete", complete_event)

            logger.info(
                f"Graph built: {node_count} nodes, {edge_count} edges, "
                f"{community_count} communities"
            )

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error building graph: {e}", exc_info=True)
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
        logger.info(f"Starting graph worker with concurrency {WORKER_CONCURRENCY}")

        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Connect
        self.connect()

        # Start consuming
        self.channel.basic_consume(
            queue="document.graph.build",
            on_message_callback=self.on_graph_build,
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
    worker = GraphWorker()
    worker.start()


if __name__ == "__main__":
    main()
