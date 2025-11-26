"""Unified event system for the application."""

# Core event broadcasting functions
from src.domains.workspaces.chats.events import CHAT_EVENT_HANDLERS

# Domain-specific event handlers
from src.domains.workspaces.documents.events import DOCUMENT_EVENT_HANDLERS
from src.domains.workspaces.events import WORKSPACE_EVENT_HANDLERS
from src.infrastructure.events.events import (
    broadcast_document_status,
    broadcast_workspace_status,
    emit_wikipedia_fetch_status,
)

# Event handler registry
from src.infrastructure.events.handlers import (
    dispatch_event,
    event_registry,
    register_event_handler,
    unregister_event_handler,
)

# Event types and data structures
from src.infrastructure.events.types import (  # Document events; Workspace events; Chat events; System events; Legacy types for backward compatibility
    ChatErrorData,
    ChatMessageData,
    ChatResponseCompleteData,
    ChatResponseData,
    DocumentChunkedData,
    DocumentEmbeddedData,
    DocumentIndexedData,
    DocumentParsedData,
    DocumentProcessingData,
    DocumentStatusData,
    LegacyDocumentStatusData,
    LegacyWorkspaceStatusData,
    SystemHealthData,
    WorkerTaskData,
    WorkspaceOperationCompleteData,
    WorkspaceStatusData,
)

# Event processing handlers (now in domains)
# from src.domains.workspaces.documents.events import (
#     handle_document_embedded,
#     handle_document_indexed,
#     handle_document_parsed,
#     handle_document_chunked,
# )


def register_domain_event_handlers(socketio) -> None:
    """
    Register all domain event handlers with the event registry.

    This function should be called during application initialization to set up
    event handling for domain-specific events.

    Args:
        socketio: SocketIO instance for broadcasting events
    """
    # Register document event handlers
    for event_type, handler in DOCUMENT_EVENT_HANDLERS.items():
        register_event_handler(event_type, lambda data, h=handler, s=socketio: h(data, s))

    # Register workspace event handlers
    for event_type, handler in WORKSPACE_EVENT_HANDLERS.items():
        register_event_handler(event_type, lambda data, h=handler, s=socketio: h(data, s))

    # Register chat event handlers
    for event_type, handler in CHAT_EVENT_HANDLERS.items():
        register_event_handler(event_type, lambda data, h=handler, s=socketio: h(data, s))


__all__ = [
    # Broadcasting functions
    "broadcast_document_status",
    "broadcast_workspace_status",
    "emit_wikipedia_fetch_status",
    # Event types
    "DocumentStatusData",
    "DocumentProcessingData",
    "DocumentParsedData",
    "DocumentChunkedData",
    "DocumentEmbeddedData",
    "DocumentIndexedData",
    "WorkspaceStatusData",
    "WorkspaceOperationCompleteData",
    "ChatMessageData",
    "ChatResponseData",
    "ChatResponseCompleteData",
    "ChatErrorData",
    "SystemHealthData",
    "WorkerTaskData",
    "LegacyDocumentStatusData",
    "LegacyWorkspaceStatusData",
    # Handler registry
    "dispatch_event",
    "event_registry",
    "register_event_handler",
    "unregister_event_handler",
    # Domain handlers
    "DOCUMENT_EVENT_HANDLERS",
    "WORKSPACE_EVENT_HANDLERS",
    "CHAT_EVENT_HANDLERS",
    # Registration function
    "register_domain_event_handlers",
]
