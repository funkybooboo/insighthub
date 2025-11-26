"""Document-specific event handlers and broadcasting functions."""

from flask import g
from flask_socketio import SocketIO

from src.infrastructure.events.events import broadcast_document_status
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def handle_document_status_update(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document status update events.

    This is called when document processing status changes.
    """
    try:
        # Broadcast the status update via WebSocket
        broadcast_document_status(event_data, socketio)

        # Log the status change
        document_id = event_data.get("document_id")
        status = event_data.get("status")
        logger.info(f"Document {document_id} status updated to: {status}")

    except Exception as e:
        logger.error(f"Failed to handle document status update: {e}")


def handle_document_processing_step(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document processing step events.

    Called when a document moves to the next processing step.
    """
    try:
        document_id = event_data.get("document_id")
        step = event_data.get("step")
        logger.info(f"Document {document_id} processing step: {step}")

        # Could add additional logic here for specific processing steps
        # For now, just broadcast the event
        broadcast_document_status(event_data, socketio)

    except Exception as e:
        logger.error(f"Failed to handle document processing step: {e}")


def _update_document_status(
    document_id: int, status: str, error_message: str | None = None, chunk_count: int | None = None
) -> None:
    """Update document status in database."""
    try:
        if hasattr(g, "app_context") and hasattr(g.app_context, "document_service"):
            document_service = g.app_context.document_service
            # Update processing status
            document_service.update_document_status(
                document_id=document_id,
                status=status,
                error_message=error_message,
                chunk_count=chunk_count,
            )
    except Exception as e:
        logger.warning(f"Failed to update document status in database: {e}")


def handle_document_parsed(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document.parsed event from parser worker.

    Updates document status to 'parsed' and broadcasts via WebSocket.
    """
    try:
        document_id_str = event_data.get("document_id")
        if not document_id_str:
            logger.error("Missing document_id in parsed event")
            return

        document_id = int(document_id_str)
        workspace_id = event_data.get("workspace_id")
        text_length = event_data.get("text_length", 0)

        logger.info(f"Document parsed: {document_id}, length: {text_length}")

        # Update document status in database (workers should have done this, but ensure it's set)
        _update_document_status(document_id, "parsed")

        # Broadcast status update via WebSocket
        status_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "status": "parsed",
            "message": f"Document parsed successfully ({text_length} characters)",
            "filename": event_data.get("filename", ""),
            "user_id": event_data.get("user_id"),
            "chunk_count": None,
        }
        broadcast_document_status(status_data, socketio)

    except Exception as e:
        logger.error(f"Error handling document.parsed event: {e}")


def handle_document_chunked(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document.chunked event from chucker worker.

    Updates document status to 'chunked' and broadcasts via WebSocket.
    """
    try:
        document_id_str = event_data.get("document_id")
        if not document_id_str:
            logger.error("Missing document_id in chunked event")
            return

        document_id = int(document_id_str)
        workspace_id = event_data.get("workspace_id")
        chunk_count = event_data.get("chunk_count", 0)

        logger.info(f"Document chunked: {document_id}, chunks: {chunk_count}")

        # Update document status in database
        _update_document_status(document_id, "chunked", chunk_count=chunk_count)

        # Broadcast status update via WebSocket
        status_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "status": "chunked",
            "message": f"Document split into {chunk_count} chunks",
            "filename": event_data.get("filename", ""),
            "user_id": event_data.get("user_id"),
            "chunk_count": chunk_count,
        }
        broadcast_document_status(status_data, socketio)

    except Exception as e:
        logger.error(f"Error handling document.chunked event: {e}")


def handle_document_embedded(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document.embedded event from embedder worker.

    Updates document status to 'embedded' and broadcasts via WebSocket.
    """
    try:
        document_id_str = event_data.get("document_id")
        if not document_id_str:
            logger.error("Missing document_id in embedded event")
            return

        document_id = int(document_id_str)
        workspace_id = event_data.get("workspace_id")
        embedding_count = event_data.get("embedding_count", 0)

        logger.info(f"Document embedded: {document_id}, embeddings: {embedding_count}")

        # Update document status in database
        _update_document_status(document_id, "embedded", chunk_count=embedding_count)

        # Broadcast status update via WebSocket
        status_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "status": "embedded",
            "message": f"Generated {embedding_count} embeddings",
            "filename": event_data.get("filename", ""),
            "user_id": event_data.get("user_id"),
            "chunk_count": embedding_count,
        }
        broadcast_document_status(status_data, socketio)

    except Exception as e:
        logger.error(f"Error handling document.embedded event: {e}")


def handle_document_indexed(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle document.indexed event from indexer worker.

    Updates document status to 'ready' and broadcasts via WebSocket.
    """
    try:
        document_id_str = event_data.get("document_id")
        if not document_id_str:
            logger.error("Missing document_id in indexed event")
            return

        document_id = int(document_id_str)
        workspace_id = event_data.get("workspace_id")
        chunk_count = event_data.get("chunk_count", 0)
        collection_name = event_data.get("collection_name", "")

        logger.info(f"Document indexed: {document_id}, collection: {collection_name}")

        # Update document status in database
        _update_document_status(document_id, "ready", chunk_count=chunk_count)

        # Broadcast status update via WebSocket
        status_data = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "status": "ready",
            "message": "Document indexed and ready for queries",
            "filename": event_data.get("filename", ""),
            "user_id": event_data.get("user_id"),
            "chunk_count": chunk_count,
        }
        broadcast_document_status(status_data, socketio)

        # Auto-retry any pending RAG queries for this workspace
        if workspace_id and event_data.get("user_id"):
            try:
                if hasattr(g, "app_context") and hasattr(g.app_context, "chat_service"):
                    chat_service = g.app_context.chat_service
                    chat_service.retry_pending_rag_queries(
                        workspace_id=int(workspace_id),
                        user_id=int(event_data["user_id"]),
                    )
            except Exception as retry_error:
                logger.warning(f"Failed to retry pending RAG queries: {retry_error}")

    except Exception as e:
        logger.error(f"Error handling document.indexed event: {e}")


# Event handler mappings for automatic registration
DOCUMENT_EVENT_HANDLERS = {
    "document.status.updated": handle_document_status_update,
    "document.processing.step": handle_document_processing_step,
    "document.parsed": handle_document_parsed,
    "document.chunked": handle_document_chunked,
    "document.embedded": handle_document_embedded,
    "document.indexed": handle_document_indexed,
}
