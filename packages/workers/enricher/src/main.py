"""
Enrichment Worker

Enriches documents with Wikipedia knowledge using Model Context Protocol (MCP).

Responsibilities:
- Consumes document.uploaded events
- Identifies key entities/concepts from documents
- Queries Wikipedia MCP server for related content
- Publishes enrichment results for downstream processing

Event Flow:
- Consumes: document.uploaded
- Publishes: document.enriched, document.enrichment.failed
"""

import json
import logging
import os
import signal
import sys
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

# TODO: Add shared package imports when implementing
# from shared.events import DocumentUploadedEvent, DocumentEnrichedEvent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE", "insighthub")

# Wikipedia MCP Configuration
MCP_WIKIPEDIA_ENDPOINT = os.getenv("MCP_WIKIPEDIA_ENDPOINT", "http://localhost:8080")

# Global connection and channel
connection: BlockingConnection | None = None
channel: BlockingChannel | None = None


def connect_rabbitmq() -> tuple[BlockingConnection, BlockingChannel]:
    """
    Establish connection to RabbitMQ.

    TODO: Implement connection logic with credentials
    TODO: Add retry logic with exponential backoff
    TODO: Declare exchange (topic exchange)
    TODO: Declare queues for document.uploaded routing
    TODO: Bind queues to exchange with routing keys

    Returns:
        Tuple of (connection, channel)
    """
    # TODO: Implement
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials, heartbeat=600
    )

    logger.info(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    # TODO: Add actual connection code
    raise NotImplementedError("RabbitMQ connection not implemented")


def extract_entities(text: str) -> list[str]:
    """
    Extract key entities/concepts from document text.

    TODO: Implement entity extraction logic
    TODO: Use NLP techniques (spaCy, NLTK, or LLM-based extraction)
    TODO: Filter entities by relevance and type
    TODO: Return list of entity strings

    Args:
        text: Document text content

    Returns:
        List of extracted entity strings
    """
    # TODO: Implement
    logger.info("Extracting entities from document text")
    return []


def query_wikipedia_mcp(entity: str) -> dict[str, Any] | None:
    """
    Query Wikipedia MCP server for entity information.

    TODO: Implement MCP protocol communication
    TODO: Send search query for entity
    TODO: Parse Wikipedia results (summary, categories, links)
    TODO: Handle errors and rate limiting
    TODO: Return structured Wikipedia data

    Args:
        entity: Entity name to search for

    Returns:
        Wikipedia data dictionary or None if not found
    """
    # TODO: Implement
    logger.info(f"Querying Wikipedia MCP for entity: {entity}")
    return None


def enrich_document(document_id: int, text: str) -> dict[str, Any]:
    """
    Enrich document with Wikipedia knowledge.

    TODO: Extract entities from document text
    TODO: Query Wikipedia for each entity
    TODO: Aggregate enrichment results
    TODO: Build enrichment metadata structure
    TODO: Return enriched document data

    Args:
        document_id: Document ID
        text: Document text content

    Returns:
        Enrichment results dictionary
    """
    # TODO: Implement
    logger.info(f"Enriching document {document_id}")

    entities = extract_entities(text)
    enrichments = []

    for entity in entities:
        wiki_data = query_wikipedia_mcp(entity)
        if wiki_data:
            enrichments.append({"entity": entity, "data": wiki_data})

    return {
        "document_id": document_id,
        "enrichments": enrichments,
        "entity_count": len(entities),
        "enrichment_count": len(enrichments),
    }


def publish_event(routing_key: str, event_data: dict[str, Any]) -> None:
    """
    Publish event to RabbitMQ exchange.

    TODO: Serialize event_data to JSON
    TODO: Publish to exchange with routing_key
    TODO: Set message properties (persistent delivery)
    TODO: Add error handling

    Args:
        routing_key: Routing key for message
        event_data: Event payload dictionary
    """
    global channel
    if not channel:
        logger.error("Channel not initialized")
        return

    # TODO: Implement
    logger.info(f"Publishing event with routing_key={routing_key}")


def process_document_uploaded(event_data: dict[str, Any]) -> None:
    """
    Process document.uploaded event.

    TODO: Extract document_id and text from event_data
    TODO: Validate event data structure
    TODO: Call enrich_document()
    TODO: Publish document.enriched event on success
    TODO: Publish document.enrichment.failed on error
    TODO: Add comprehensive error handling

    Args:
        event_data: Event payload from RabbitMQ
    """
    try:
        # TODO: Implement
        logger.info(f"Processing document.uploaded event: {event_data}")

        document_id = event_data.get("document_id")
        text = event_data.get("text")

        if not document_id or not text:
            logger.error("Missing required fields in event")
            return

        # Enrich document
        enrichment_result = enrich_document(document_id, text)

        # Publish success event
        publish_event(
            "document.enriched",
            {
                "document_id": document_id,
                "enrichments": enrichment_result["enrichments"],
                "metadata": {
                    "entity_count": enrichment_result["entity_count"],
                    "enrichment_count": enrichment_result["enrichment_count"],
                },
            },
        )

    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        # Publish failure event
        publish_event(
            "document.enrichment.failed",
            {"document_id": event_data.get("document_id"), "error": str(e)},
        )


def on_message(
    ch: BlockingChannel, method: pika.spec.Basic.Deliver, properties: Any, body: bytes
) -> None:
    """
    RabbitMQ message callback.

    TODO: Deserialize message body from JSON
    TODO: Route to appropriate handler based on routing_key
    TODO: Acknowledge message after processing
    TODO: Add error handling and message rejection on failures

    Args:
        ch: Channel
        method: Delivery method
        properties: Message properties
        body: Message body (JSON bytes)
    """
    try:
        event_data = json.loads(body)
        routing_key = method.routing_key

        logger.info(f"Received message with routing_key={routing_key}")

        if routing_key == "document.uploaded":
            process_document_uploaded(event_data)

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        # Reject message (don't requeue to avoid infinite loops)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer() -> None:
    """
    Start consuming messages from RabbitMQ.

    TODO: Set QoS for prefetch_count (limit concurrent processing)
    TODO: Register message callback
    TODO: Start consuming (blocking call)
    TODO: Add error handling
    """
    global channel
    if not channel:
        logger.error("Channel not initialized")
        return

    # TODO: Implement
    logger.info("Starting enrichment worker consumer")


def shutdown(signum: int, frame: Any) -> None:
    """
    Graceful shutdown handler.

    TODO: Stop consuming messages
    TODO: Close channel
    TODO: Close connection
    TODO: Exit process

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    global connection, channel

    # TODO: Implement shutdown logic
    sys.exit(0)


def main() -> None:
    """
    Main entry point for enrichment worker.

    TODO: Register signal handlers (SIGTERM, SIGINT)
    TODO: Connect to RabbitMQ
    TODO: Start consumer (blocking)
    TODO: Handle unexpected errors
    """
    global connection, channel

    # Register signal handlers
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info("Starting Enrichment Worker")

    try:
        # Connect to RabbitMQ
        connection, channel = connect_rabbitmq()

        # Start consuming
        start_consumer()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
