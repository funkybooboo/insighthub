"""
Notifier Worker - WebSocket notification broadcasting.

Sends notifications to clients via WebSocket when events occur.

Consumes: *.uploaded, *.completed, *.failed, *.response (wildcard patterns)
Produces: WebSocket messages to connected clients
"""

import os
from dataclasses import dataclass

from shared.logger import create_logger
from shared.types.common import MetadataDict, PayloadDict
from shared.worker import Worker

logger = create_logger(__name__)

# Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))

# WebSocket Configuration
WEBSOCKET_SERVER = os.getenv("WEBSOCKET_SERVER", "http://localhost:5000")


@dataclass
class NotificationPayload:
    """Payload for WebSocket notifications."""

    event_type: str
    user_id: int | None
    workspace_id: str | None
    data: PayloadDict
    metadata: MetadataDict


class NotifierWorker(Worker):
    """Notifier worker for WebSocket broadcasting."""

    def __init__(self) -> None:
        """Initialize the notifier worker."""
        super().__init__(
            worker_name="notifier",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="#",  # Subscribe to all events
            consume_queue="notifier.all",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self._websocket_server = WEBSOCKET_SERVER
        self._websocket_client = self._connect_websocket()

    def _connect_websocket(self) -> object | None:
        """
        Connect to WebSocket server for broadcasting.

        TODO: Implement WebSocket connection:
        1. Initialize Socket.IO client
        2. Connect to server
        3. Add authentication if needed
        4. Handle connection errors

        Returns:
            Socket.IO client instance or None
        """
        logger.info("Connecting to WebSocket server", server=self._websocket_server)
        # TODO: Implement WebSocket connection
        # import socketio
        # sio = socketio.Client()
        # sio.connect(self._websocket_server)
        # return sio
        return None

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process incoming events and broadcast to clients.

        Args:
            event_data: Parsed event data as dictionary
        """
        # Extract routing key from metadata if available
        routing_key = str(event_data.get("_routing_key", "unknown"))
        user_id = event_data.get("user_id")
        workspace_id = event_data.get("workspace_id")
        metadata = dict(event_data.get("metadata", {}))

        logger.info(
            "Processing notification event",
            routing_key=routing_key,
            user_id=user_id,
        )

        # Route to appropriate handler based on event type
        if routing_key == "document.uploaded":
            self._handle_document_uploaded(event_data)
        elif routing_key == "embeddings.completed" or routing_key == "vector.index.updated":
            self._handle_embeddings_completed(event_data)
        elif routing_key == "document.graph.built":
            self._handle_graph_built(event_data)
        elif routing_key == "query.response":
            self._handle_query_response(event_data)
        elif ".failed" in routing_key:
            self._handle_error_event(routing_key, event_data)
        else:
            logger.debug("Unhandled event type", routing_key=routing_key)

        # Create notification payload
        notification = NotificationPayload(
            event_type=routing_key,
            user_id=int(user_id) if user_id else None,
            workspace_id=str(workspace_id) if workspace_id else None,
            data=event_data,
            metadata=metadata,
        )

        # Broadcast to appropriate clients
        if notification.user_id:
            self._broadcast_to_user(notification.user_id, notification)
        else:
            self._broadcast_to_all(notification)

    def _handle_document_uploaded(self, event_data: PayloadDict) -> None:
        """
        Handle document.uploaded event.

        Args:
            event_data: Event payload
        """
        logger.info(
            "Document uploaded notification",
            document_id=event_data.get("document_id"),
            filename=event_data.get("filename"),
        )

    def _handle_embeddings_completed(self, event_data: PayloadDict) -> None:
        """
        Handle embeddings.completed event.

        Args:
            event_data: Event payload
        """
        logger.info(
            "Embeddings completed notification",
            document_id=event_data.get("document_id"),
            chunk_count=event_data.get("chunk_count"),
        )

    def _handle_graph_built(self, event_data: PayloadDict) -> None:
        """
        Handle document.graph.built event.

        Args:
            event_data: Event payload
        """
        logger.info(
            "Graph built notification",
            document_id=event_data.get("document_id"),
        )

    def _handle_query_response(self, event_data: PayloadDict) -> None:
        """
        Handle query.response event.

        Args:
            event_data: Event payload
        """
        logger.info(
            "Query response notification",
            session_id=event_data.get("session_id"),
        )

    def _handle_error_event(self, routing_key: str, event_data: PayloadDict) -> None:
        """
        Handle error events (*.failed).

        Args:
            routing_key: Event routing key
            event_data: Event payload
        """
        logger.warning(
            "Error event notification",
            routing_key=routing_key,
            error=event_data.get("error"),
        )

    def _broadcast_to_user(self, user_id: int, notification: NotificationPayload) -> None:
        """
        Broadcast notification to specific user via WebSocket.

        TODO: Implement user-targeted broadcasting:
        1. Get Socket.IO client instance
        2. Construct notification message
        3. Emit to user's room/namespace
        4. Handle disconnected clients

        Args:
            user_id: User ID to send notification to
            notification: Notification payload
        """
        logger.info(
            "Broadcasting to user",
            user_id=user_id,
            event_type=notification.event_type,
        )
        # TODO: Implement user broadcasting
        # if self._websocket_client:
        #     self._websocket_client.emit(
        #         "notification",
        #         {
        #             "type": notification.event_type,
        #             "data": notification.data,
        #         },
        #         room=f"user_{user_id}"
        #     )

    def _broadcast_to_all(self, notification: NotificationPayload) -> None:
        """
        Broadcast notification to all connected clients.

        TODO: Implement global broadcasting:
        1. Get Socket.IO client instance
        2. Construct notification message
        3. Emit to global namespace
        4. Handle errors

        Args:
            notification: Notification payload
        """
        logger.info(
            "Broadcasting to all users",
            event_type=notification.event_type,
        )
        # TODO: Implement global broadcasting
        # if self._websocket_client:
        #     self._websocket_client.emit(
        #         "notification",
        #         {
        #             "type": notification.event_type,
        #             "data": notification.data,
        #         }
        #     )


def main() -> None:
    """Main entry point for notifier worker."""
    worker = NotifierWorker()
    worker.start()


if __name__ == "__main__":
    main()
