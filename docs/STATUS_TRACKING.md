# Status Tracking System

## Overview

InsightHub implements a comprehensive status tracking system for long-running operations (document processing, workspace provisioning) with real-time UI updates. The system follows proper OOP principles with shared logic in the shared library.

## Architecture

```
User Action → Server API → Database (status: pending) → RabbitMQ Event
                                                              ↓
                                                           Worker
                                                              ↓
                                         StatusService.update_status()
                                                              ↓
                                         Database (status: processing/ready/failed)
                                                              ↓
                                         RabbitMQ Event (status.updated)
                                                              ↓
                                         Server WebSocket Broadcast
                                                              ↓
                                              Client UI Updates in Real-Time
```

## Database Models

### Document Status Fields
```python
processing_status: str  # 'pending', 'processing', 'ready', 'failed'
processing_error: str | None  # Error message for failed status
```

### Workspace Status Fields
```python
status: str  # 'provisioning', 'ready', 'error'
status_message: str | None  # Optional status message
```

## Shared Library Components

### 1. Status Enums (`shared/types/status.py`)
```python
class DocumentProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class WorkspaceStatus(str, Enum):
    PROVISIONING = "provisioning"
    READY = "ready"
    ERROR = "error"
```

### 2. Result Type (`shared/types/result.py`)
```python
# Instead of returning None or raising exceptions
Result[T, E] = Ok[T] | Err[E]

# Usage:
result = service.update_status(...)
if result.is_ok():
    document = result.unwrap()
else:
    error = result.error
```

### 3. StatusRepository Interface (`shared/repositories/status.py`)
```python
class StatusRepository(ABC):
    @abstractmethod
    def update_document_status(...) -> Document | None: pass
    
    @abstractmethod
    def update_workspace_status(...) -> Workspace | None: pass

class SqlStatusRepository(StatusRepository):
    # SQL implementation using SQLAlchemy
```

### 4. StatusService (`shared/services/status_service.py`)
```python
class StatusService:
    """
    Coordinates status updates with event publishing.
    Follows Single Responsibility Principle.
    """
    def __init__(
        self,
        status_repository: StatusRepository,
        message_publisher: RabbitMQPublisher | None
    ): ...
    
    def update_document_status(...) -> Result[Document, str]: ...
    def update_workspace_status(...) -> Result[Workspace, str]: ...
```

## Worker Usage Example

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.messaging.publisher import RabbitMQPublisher
from shared.repositories.status import SqlStatusRepository
from shared.services.status_service import StatusService
from shared.types.status import DocumentProcessingStatus

# Initialize dependencies (once per worker)
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

publisher = RabbitMQPublisher(
    rabbitmq_url=os.getenv("RABBITMQ_URL"),
    exchange=os.getenv("RABBITMQ_EXCHANGE")
)

status_repo = SqlStatusRepository(db)
status_service = StatusService(status_repo, publisher)

# In your message handler
def handle_document_uploaded(event):
    document_id = event["document_id"]
    
    # Mark as processing
    result = status_service.update_document_status(
        document_id=document_id,
        status=DocumentProcessingStatus.PROCESSING
    )
    
    if result.is_err():
        logger.error(f"Failed to update status: {result.error}")
        return
    
    try:
        # Do actual work (parse, chunk, embed, index)
        chunks = process_document(event["file_path"])
        
        # Mark as ready
        status_service.update_document_status(
            document_id=document_id,
            status=DocumentProcessingStatus.READY,
            chunk_count=len(chunks),
            metadata={"embedding_model": "nomic-embed-text"}
        )
    except Exception as e:
        # Mark as failed
        status_service.update_document_status(
            document_id=document_id,
            status=DocumentProcessingStatus.FAILED,
            error=str(e)
        )
```

## Client Components

### 1. Shared UI Components (`packages/client/src/components/shared/`)

#### LoadingSpinner.tsx
```tsx
<LoadingSpinner size="sm" | "md" | "lg" />
```

#### StatusBadge.tsx
```tsx
<StatusBadge 
    status="pending" | "processing" | "provisioning" | "ready" | "failed" | "error"
    message="Optional message"
    size="sm" | "md"
/>
```

#### ProgressIndicator.tsx
```tsx
<ProgressIndicator
    title="Processing document..."
    description="This may take a few minutes"
    steps={[
        { label: "Parsing PDF", completed: true },
        { label: "Chunking text", completed: true },
        { label: "Generating embeddings", completed: false },
        { label: "Indexing to vector store", completed: false }
    ]}
/>
```

### 2. WebSocket Status Updates (Server Side)

The server should listen for `document.status.updated` and `workspace.status.updated` events from RabbitMQ and broadcast them to connected clients:

```python
# In server socket handler
@socketio.on('connect')
def handle_connect():
    user_id = get_current_user_id()
    join_room(f"user_{user_id}")

# RabbitMQ consumer (separate thread/process)
def on_status_update(event):
    if event["routing_key"] == "document.status.updated":
        socketio.emit(
            "document_status",
            event["message"],
            room=f"user_{event['message']['user_id']}"
        )
    elif event["routing_key"] == "workspace.status.updated":
        socketio.emit(
            "workspace_status",
            event["message"],
            room=f"user_{event['message']['user_id']}"
        )
```

### 3. Client WebSocket Listeners

```tsx
import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { socket } from '../services/socket';

export function useStatusUpdates() {
    const dispatch = useDispatch();
    
    useEffect(() => {
        socket.on('document_status', (data) => {
            dispatch(updateDocumentStatus(data));
        });
        
        socket.on('workspace_status', (data) => {
            dispatch(updateWorkspaceStatus(data));
        });
        
        return () => {
            socket.off('document_status');
            socket.off('workspace_status');
        };
    }, [dispatch]);
}
```

## OOP Principles Applied

### 1. **Program to Interfaces, Not Implementations**
- `StatusRepository` is an abstract class
- `SqlStatusRepository` is a concrete implementation
- Workers/services depend on `StatusRepository`, not `SqlStatusRepository`

### 2. **Dependency Injection**
- `StatusService` receives `StatusRepository` and `RabbitMQPublisher` via constructor
- No instantiation of dependencies inside classes
- Easy to test with mocks/dummies

### 3. **Single Responsibility Principle**
- `StatusRepository`: Database operations only
- `StatusService`: Orchestrates status updates + event publishing
- `RabbitMQPublisher`: Message publishing only

### 4. **Result Type Instead of Exceptions**
- Methods return `Result[T, E]` instead of `T | None`
- Explicit error handling
- No silent failures
- Can still raise exceptions for truly exceptional cases

### 5. **Type Safety**
- Status values are enums, not magic strings
- Type annotations throughout
- MyPy strict mode compatible

## Database Migrations

Three migrations created:

1. **`3a98e52c2212_add_workspace_and_rag_config_tables.py`**
   - Creates `workspaces` and `rag_configs` tables

2. **`944e0ffe0f5e_add_default_rag_config_table.py`**
   - Creates `default_rag_configs` table for user default RAG settings

3. **`f3cc95ed95dd_add_status_fields_to_workspace_and_.py`**
   - Adds `status`, `status_message` to workspaces
   - Adds `processing_status`, `processing_error` to documents
   - Creates indexes on status fields

Run migrations:
```bash
cd packages/server
poetry run alembic upgrade head
```

## Next Steps

### Server Implementation
1. Add RabbitMQ consumer to listen for `*.status.updated` events
2. Broadcast status updates via WebSocket to connected clients
3. Add WebSocket event handlers in `socket_handlers.py`

### Client Implementation
1. Create workspace list/detail pages with status indicators
2. Create document upload UI with processing status
3. Add WebSocket listeners for real-time updates
4. Show ProgressIndicator during long operations

### Worker Implementation
1. Update ingestion worker to use `StatusService`
2. Update embeddings worker to use `StatusService`
3. Update graph worker to use `StatusService`
4. Test end-to-end status flow

## Testing

### Unit Tests
```python
def test_status_service_updates_document():
    # Use dummy repository
    repo = DummyStatusRepository()
    service = StatusService(repo, None)  # No publisher for unit test
    
    result = service.update_document_status(
        document_id=1,
        status=DocumentProcessingStatus.READY
    )
    
    assert result.is_ok()
    assert result.unwrap().processing_status == "ready"

def test_status_service_returns_error_for_missing_document():
    repo = DummyStatusRepository()  # Returns None
    service = StatusService(repo, None)
    
    result = service.update_document_status(
        document_id=999,
        status=DocumentProcessingStatus.READY
    )
    
    assert result.is_err()
    assert "not found" in result.error
```

### Integration Tests
```python
def test_worker_updates_status(db, rabbitmq):
    # Test with real database and RabbitMQ
    publisher = RabbitMQPublisher(...)
    repo = SqlStatusRepository(db)
    service = StatusService(repo, publisher)
    
    # Create test document
    doc = create_test_document(db, status="pending")
    
    # Update status
    result = service.update_document_status(
        document_id=doc.id,
        status=DocumentProcessingStatus.PROCESSING
    )
    
    # Verify database updated
    db.refresh(doc)
    assert doc.processing_status == "processing"
    
    # Verify event published
    event = rabbitmq.get_next_message()
    assert event["routing_key"] == "document.status.updated"
    assert event["message"]["document_id"] == doc.id
```
