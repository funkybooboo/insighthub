"""
Wikipedia Worker - Fetches content from Wikipedia and creates documents.

Consumes: wikipedia.fetch_requested
Produces: document.uploaded (for each created document)
"""

import os
from dataclasses import asdict, dataclass
from typing import Any

import pika
import psycopg2
import wikipediaapi
import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insighthub:insighthub_dev@postgres:5432/insighthub")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "insighthub")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "insighthub_dev_secret")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "documents")


@dataclass
class WikipediaFetchStatusEvent:
    """Event emitted during Wikipedia fetching."""

    workspace_id: str
    query: str
    status: str  # 'fetching', 'processing', 'completed', 'failed'
    document_ids: list[str]
    message: str
    metadata: dict[str, Any]


class Worker:
    """Base worker class for RabbitMQ message processing."""

    def __init__(
        self,
        worker_name: str,
        rabbitmq_url: str,
        exchange: str,
        exchange_type: str,
        consume_routing_key: str,
        consume_queue: str,
        prefetch_count: int = 1,
    ):
        self.worker_name = worker_name
        self.rabbitmq_url = rabbitmq_url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.consume_routing_key = consume_routing_key
        self.consume_queue = consume_queue
        self.prefetch_count = prefetch_count
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.channel.Channel | None = None

    def start(self) -> None:
        """Start the worker."""
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True
        )

        # Declare queue
        self.channel.queue_declare(queue=self.consume_queue, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=self.consume_queue,
            routing_key=self.consume_routing_key
        )

        # Set prefetch count
        self.channel.basic_qos(prefetch_count=self.prefetch_count)

        # Start consuming
        self.channel.basic_consume(
            queue=self.consume_queue,
            on_message_callback=self._on_message
        )

        logger.info(f"Started {self.worker_name} worker")
        self.channel.start_consuming()

    def stop(self) -> None:
        """Stop the worker."""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()

    def _on_message(
        self,
        ch: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
        """Handle incoming message."""
        try:
            import json
            event_data = json.loads(body.decode('utf-8'))
            self.process_event(event_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process the event. Override in subclasses."""
        raise NotImplementedError

    def publish_event(self, routing_key: str, event_data: dict[str, Any]) -> None:
        """Publish an event to RabbitMQ."""
        if not self.channel:
            raise RuntimeError("Worker not started")

        import json
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=json.dumps(event_data).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(DATABASE_URL)


class WikipediaFetcher:
    """Fetches content from Wikipedia."""

    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='InsightHub/1.0 (https://github.com/nstott/insighthub)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def search_and_fetch(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        """
        Search for Wikipedia pages and fetch their content.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of page data with title, summary, and full content
        """
        results = []

        try:
            # First, search for pages
            search_results = self.wiki.search(query, results=max_results)

            for title in search_results[:max_results]:
                try:
                    page = self.wiki.page(title)

                    if page.exists():
                        # Get a reasonable summary (first few paragraphs)
                        content = page.summary
                        if len(content) < 500:  # If summary is too short, get more content
                            # Get first few sections
                            sections = page.sections
                            for section in sections[:3]:  # First 3 sections
                                if section.title not in ['References', 'External links', 'See also']:
                                    content += f"\n\n{section.title}\n{section.text}"
                                    if len(content) > 2000:  # Limit content length
                                        break

                        results.append({
                            'title': page.title,
                            'url': page.fullurl,
                            'content': content[:5000],  # Limit to 5000 chars
                            'summary': page.summary[:500] if page.summary else '',
                            'page_id': page.pageid
                        })

                except Exception as e:
                    logger.warning(f"Failed to fetch page '{title}': {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to search Wikipedia for '{query}': {e}")

        return results


class WikipediaWorker(Worker):
    """Wikipedia fetch worker."""

    def __init__(self) -> None:
        """Initialize the Wikipedia worker."""
        super().__init__(
            worker_name="wikipedia",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="wikipedia.fetch_requested",
            consume_queue="wikipedia.wikipedia.fetch_requested",
            prefetch_count=WORKER_CONCURRENCY,
        )

        # Initialize Wikipedia fetcher
        self.fetcher = WikipediaFetcher()

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process wikipedia.fetch_requested event.

        Args:
            event_data: Event data containing workspace_id, query, etc.
        """
        workspace_id = str(event_data.get("workspace_id", ""))
        query = str(event_data.get("query", ""))
        user_id = str(event_data.get("user_id", ""))

        logger.info(
            "Fetching content from Wikipedia",
            extra={
                "workspace_id": workspace_id,
                "query": query
            }
        )

        try:
            # Publish initial status
            self._publish_status_event(workspace_id, query, "fetching", "Searching Wikipedia...", [])

            # Fetch content from Wikipedia
            pages = self.fetcher.search_and_fetch(query)

            if not pages:
                # Publish failure status
                self._publish_status_event(workspace_id, query, "failed", "No Wikipedia pages found", [])
                return

            # Publish processing status
            self._publish_status_event(workspace_id, query, "processing", f"Processing {len(pages)} pages...", [])

            # Create documents from pages
            document_ids = []
            for page in pages:
                try:
                    doc_id = self._create_document_from_page(workspace_id, user_id, page)
                    document_ids.append(doc_id)

                    # Publish document.uploaded event for each document
                    self._publish_document_uploaded_event(workspace_id, doc_id, page)

                except Exception as e:
                    logger.error(f"Failed to create document from page '{page['title']}': {e}")
                    continue

            # Publish completion status
            self._publish_status_event(workspace_id, query, "completed", f"Created {len(document_ids)} documents", document_ids)

            logger.info(
                "Successfully fetched Wikipedia content",
                extra={
                    "workspace_id": workspace_id,
                    "query": query,
                    "pages_found": len(pages),
                    "documents_created": len(document_ids)
                }
            )

        except Exception as e:
            logger.error(
                "Failed to fetch Wikipedia content",
                extra={
                    "workspace_id": workspace_id,
                    "query": query,
                    "error": str(e)
                }
            )
            # Publish failure status
            self._publish_status_event(workspace_id, query, "failed", f"Failed to fetch content: {str(e)}", [])
            raise

    def _create_document_from_page(self, workspace_id: str, user_id: str, page: dict[str, Any]) -> str:
        """Create a document record from Wikipedia page data."""
        import uuid
        import hashlib

        doc_id = str(uuid.uuid4())
        content = page['content']
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        filename = f"wikipedia_{page['page_id']}_{page['title'].replace(' ', '_')}.txt"

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Store content in MinIO (simplified - in real implementation would use MinIO client)
                # For now, we'll store the content directly in the database
                blob_key = f"wikipedia/{content_hash[:16]}/{filename}"

                cursor.execute("""
                    INSERT INTO documents (
                        id, user_id, workspace_id, filename, file_path, file_size,
                        mime_type, content_hash, processing_status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                """, (
                    doc_id, user_id, workspace_id, filename, blob_key, len(content),
                    'text/plain', content_hash
                ))

                # Store parsed text directly
                cursor.execute("""
                    UPDATE documents SET parsed_text = %s WHERE id = %s
                """, (content, doc_id))

            conn.commit()
        finally:
            conn.close()

        return doc_id

    def _publish_document_uploaded_event(self, workspace_id: str, document_id: str, page: dict[str, Any]) -> None:
        """Publish document.uploaded event."""
        event_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "content_type": "text/plain",
            "file_path": f"wikipedia/{page['page_id']}_{page['title'].replace(' ', '_')}.txt",
            "metadata": {
                "source": "wikipedia",
                "wikipedia_url": page["url"],
                "wikipedia_page_id": page["page_id"],
                "wikipedia_title": page["title"]
            }
        }
        self.publish_event("document.uploaded", event_data)

    def _publish_status_event(self, workspace_id: str, query: str, status: str, message: str, document_ids: list[str]) -> None:
        """Publish Wikipedia fetch status event."""
        event = WikipediaFetchStatusEvent(
            workspace_id=workspace_id,
            query=query,
            status=status,
            document_ids=document_ids,
            message=message,
            metadata={}
        )
        self.publish_event("wikipedia_fetch_status", asdict(event))


def main() -> None:
    """Main entry point."""
    worker = WikipediaWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping Wikipedia worker")
        worker.stop()


if __name__ == "__main__":
    main()