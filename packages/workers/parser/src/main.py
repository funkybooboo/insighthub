"""
Parser Worker - Document text extraction.

Consumes: document.uploaded
Produces: document.parsed
"""

import io
import os
from dataclasses import asdict, dataclass
from typing import Any

import pika
from minio import Minio
from pypdf import PdfReader
from docx import Document as DocxDocument
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insighthub:insighthub_dev@postgres:5432/insighthub")
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "insighthub")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "insighthub_dev_secret")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "documents")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))


@dataclass
class DocumentParsedEvent:
    """Event emitted when document is parsed."""

    document_id: str
    workspace_id: str
    content_type: str
    text_length: int
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


class DocumentParser:
    """Document parser for various file formats."""

    def __init__(self, minio_client: Minio, bucket_name: str):
        self.minio_client = minio_client
        self.bucket_name = bucket_name

    def parse_document(self, document_id: str, content_type: str, file_path: str) -> str:
        """
        Parse document content based on content type.

        Args:
            document_id: Document ID
            content_type: MIME content type
            file_path: Path to file in MinIO

        Returns:
            Extracted text content
        """
        # Get file from MinIO
        try:
            response = self.minio_client.get_object(self.bucket_name, file_path)
            file_data = response.read()
            response.close()
            response.release_conn()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve file from MinIO: {e}")

        # Parse based on content type
        if content_type == "application/pdf":
            return self._parse_pdf(file_data)
        elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                              "application/msword"]:
            return self._parse_docx(file_data)
        elif content_type.startswith("text/html"):
            return self._parse_html(file_data)
        elif content_type.startswith("text/"):
            return self._parse_text(file_data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    def _parse_pdf(self, file_data: bytes) -> str:
        """Parse PDF file."""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF: {e}")

    def _parse_docx(self, file_data: bytes) -> str:
        """Parse DOCX file."""
        try:
            docx_file = io.BytesIO(file_data)
            doc = DocxDocument(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to parse DOCX: {e}")

    def _parse_html(self, file_data: bytes) -> str:
        """Parse HTML file."""
        try:
            soup = BeautifulSoup(file_data, 'lxml')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            return soup.get_text(separator='\n').strip()
        except Exception as e:
            raise RuntimeError(f"Failed to parse HTML: {e}")

    def _parse_text(self, file_data: bytes) -> str:
        """Parse plain text file."""
        try:
            return file_data.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Try with different encodings
            try:
                return file_data.decode('latin-1').strip()
            except Exception as e:
                raise RuntimeError(f"Failed to parse text file: {e}")


class ParserWorker(Worker):
    """Document parser worker."""

    def __init__(self) -> None:
        """Initialize the parser worker."""
        super().__init__(
            worker_name="parser",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.uploaded",
            consume_queue="parser.document.uploaded",
            prefetch_count=WORKER_CONCURRENCY,
        )

        # Initialize MinIO client
        self.minio_client = Minio(
            MINIO_ENDPOINT_URL.replace("http://", "").replace("https://", ""),
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False  # Use HTTP for local development
        )

        # Initialize database connection
        self.db_engine = create_engine(DATABASE_URL)

        # Initialize document parser
        self.parser = DocumentParser(self.minio_client, MINIO_BUCKET_NAME)

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.uploaded event to extract text.

        Args:
            event_data: Event data containing document_id, workspace_id, content_type, file_path, etc.
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        content_type = str(event_data.get("content_type", "text/plain"))
        file_path = str(event_data.get("file_path", ""))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Parsing document",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "content_type": content_type,
                "file_path": file_path
            }
        )

        try:
            # Parse the document
            text_content = self.parser.parse_document(document_id, content_type, file_path)
            text_length = len(text_content)

            # Store parsed text in database
            self._store_parsed_text(document_id, text_content)

            # Update document status
            self._update_document_status(document_id, "parsed", {"text_length": text_length})

            # Publish document.parsed event
            parsed_event = DocumentParsedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                content_type=content_type,
                text_length=text_length,
                metadata=metadata,
            )
            self.publish_event("document.parsed", asdict(parsed_event))

            logger.info(
                "Successfully parsed document",
                extra={
                    "document_id": document_id,
                    "text_length": text_length
                }
            )

        except Exception as e:
            logger.error(
                "Failed to parse document",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            # Update document status to failed
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _store_parsed_text(self, document_id: str, text_content: str) -> None:
        """Store parsed text in database."""
        with self.db_engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE documents
                    SET parsed_text = :text_content,
                        processing_status = 'parsed',
                        updated_at = NOW()
                    WHERE id = :document_id
                """),
                {"document_id": document_id, "text_content": text_content}
            )
            conn.commit()

    def _update_document_status(self, document_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        """Update document processing status."""
        with self.db_engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE documents
                    SET processing_status = :status,
                        processing_metadata = COALESCE(processing_metadata, '{}')::jsonb || :metadata::jsonb,
                        updated_at = NOW()
                    WHERE id = :document_id
                """),
                {
                    "document_id": document_id,
                    "status": status,
                    "metadata": metadata or {}
                }
            )
            conn.commit()


def main() -> None:
    """Main entry point."""
    worker = ParserWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping parser worker")
        worker.stop()


if __name__ == "__main__":
    main()
