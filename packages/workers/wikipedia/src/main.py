"""
Wikipedia Worker - Fetches content from Wikipedia and creates documents.

Consumes: wikipedia.fetch_requested
Produces: document.uploaded (for each created document)
"""

from dataclasses import asdict, dataclass
from typing import Any
import json
import uuid
import hashlib
import io

from shared.config import config
from shared.worker.worker import Worker as BaseWorker
from shared.logger import get_logger
from shared.database.sql.postgres import PostgresConnection
from shared.storage.s3_blob_storage import S3BlobStorage
import wikipediaapi

logger = get_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
WORKER_CONCURRENCY = config.worker_concurrency
MINIO_URL = config.s3_endpoint_url
MINIO_ACCESS_KEY = config.s3_access_key
MINIO_SECRET_KEY = config.s3_secret_key
MINIO_BUCKET_NAME = config.s3_bucket_name


@dataclass
class WikipediaFetchStatusEvent:
    workspace_id: str
    query: str
    status: str
    document_ids: list[str]
    message: str

class WikipediaFetcher:
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia('InsightHub/1.0', 'en')

    def search_and_fetch(self, query: str, max_results: int = 1) -> list[dict[str, Any]]:
        pages = self.wiki.search(query, results=max_results)
        results = []
        for title in pages:
            page = self.wiki.page(title)
            if page.exists():
                results.append({
                    "title": page.title,
                    "url": page.fullurl,
                    "content": page.text,
                    "summary": page.summary,
                    "page_id": page.pageid
                })
        return results

class WikipediaWorker(BaseWorker):
    """Wikipedia fetch worker."""

    def __init__(self) -> None:
        """Initialize the Wikipedia worker."""
        super().__init__(
            worker_name="wikipedia",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="wikipedia.fetch_requested",
            consume_queue="wikipedia.fetch_requested",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self.fetcher = WikipediaFetcher()
        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()
        self.blob_storage = S3BlobStorage(
            endpoint=MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            bucket_name=MINIO_BUCKET_NAME,
            secure=False,
        )

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process wikipedia.fetch_requested event.
        """
        workspace_id = str(event_data.get("workspace_id"))
        query = str(event_data.get("query"))
        user_id = str(event_data.get("user_id"))

        logger.info("Fetching content from Wikipedia", extra=event_data)

        try:
            self._publish_status(workspace_id, query, "fetching", "Searching Wikipedia...", [])
            pages = self.fetcher.search_and_fetch(query)

            if not pages:
                self._publish_status(workspace_id, query, "failed", "No Wikipedia pages found", [])
                return

            self._publish_status(workspace_id, query, "processing", f"Processing {len(pages)} pages...", [])
            
            document_ids = []
            for page in pages:
                file_path, doc_id = self._create_document_from_page(workspace_id, user_id, page)
                document_ids.append(doc_id)
                self._publish_document_uploaded_event(workspace_id, user_id, doc_id, file_path, page)

            self._publish_status(workspace_id, query, "completed", f"Created {len(document_ids)} documents", document_ids)
            logger.info("Successfully fetched Wikipedia content", extra={"workspace_id": workspace_id, "documents_created": len(document_ids)})

        except Exception as e:
            logger.error("Failed to fetch Wikipedia content", extra={"workspace_id": workspace_id, "error": str(e)})
            self._publish_status(workspace_id, query, "failed", f"Failed to fetch content: {str(e)}", [])
            raise

    def _create_document_from_page(self, workspace_id: str, user_id: str, page: dict[str, Any]) -> (str, str):
        content = page['content'].encode('utf-8')
        content_hash = hashlib.sha256(content).hexdigest()
        filename = f"wikipedia_{page['page_id']}.txt"
        file_path = f"wikipedia/{filename}"

        upload_result = self.blob_storage.upload_file(io.BytesIO(content), file_path)
        if upload_result.is_err():
            raise upload_result.unwrap_err()

        with self.db_connection.get_cursor(as_dict=True) as cursor:
            cursor.execute(
                """
                INSERT INTO documents (user_id, workspace_id, filename, file_path, file_size, mime_type, content_hash, processing_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending') RETURNING id
                """,
                (user_id, workspace_id, filename, file_path, len(content), 'text/plain', content_hash)
            )
            result = cursor.fetchone()
            self.db_connection.connection.commit()
            if not result:
                raise Exception("Failed to create document record")
            return file_path, str(result['id'])

    def _publish_document_uploaded_event(self, workspace_id: str, user_id: str, document_id: str, file_path: str, page: dict[str, Any]) -> None:
        event_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "content_type": "text/plain",
            "file_path": file_path,
            "metadata": {
                "source": "wikipedia",
                "url": page["url"],
                "title": page["title"]
            }
        }
        self.publish_event("document.uploaded", event_data)

    def _publish_status(self, workspace_id: str, query: str, status: str, message: str, document_ids: list[str]) -> None:
        event = WikipediaFetchStatusEvent(
            workspace_id=workspace_id, query=query, status=status, document_ids=document_ids, message=message
        )
        self.publish_event("wikipedia.fetch_status", asdict(event))

def main() -> None:
    worker = WikipediaWorker()
    worker.start()

if __name__ == "__main__":
    main()
