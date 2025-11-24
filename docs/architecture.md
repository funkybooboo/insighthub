# Architecture Documentation

Comprehensive overview of the InsightHub dual RAG system architecture.

## System Overview

The InsightHub system provides an interactive platform for RAG-based analysis of academic papers, comparing Vector RAG and Graph RAG approaches. It is built with a clean architecture, ensuring clear separation of concerns and maintainability.

The **React Frontend** serves as the primary user interface, offering a dynamic environment for managing workspaces, chat sessions, and documents. It provides real-time feedback on background processes (like RAG provisioning, document processing, and RAG enhancement jobs) through WebSockets, ensuring a responsive and informed user experience.

**Core Components**:
1. **React Frontend** - The interactive user interface for workspace, chat, and document management, displaying real-time status updates.
2. Flask Backend - REST API and WebSocket endpoints for client-server communication and orchestrating RAG operations.
3. RAG Engine - Pluggable retrieval/generation components, responsible for integrating external knowledge sources.
4. Vector Database - Qdrant for similarity search of document embeddings.
5. PostgreSQL - Centralized storage for application data, user profiles, and chat history.
6. LLM Providers - Integrations with various Large Language Models (Ollama, OpenAI, Claude, HuggingFace) for generating responses.

## Architecture Layers

```
+----------------------------------+
|     Presentation Layer           |
|  (API Routes, WebSocket, CLI)    |
+----------------------------------+
|      Domain Layer                |
|  (Business Logic Services)       |
+----------------------------------+
|   Infrastructure Layer           |
| (RAG, Database, Storage, LLM)    |
+----------------------------------+
```

### Presentation Layer
- **Location**: `src/domains/*/routes.py`, `src/domains/*/commands.py`
- **Purpose**: Handle HTTP/WebSocket requests and CLI commands
- **Components**: Flask routes, Socket.IO handlers, request validation

### Domain Layer
- **Location**: `src/domains/*/service.py`, `src/domains/*/models.py`
- **Purpose**: Business logic and domain models
- **Components**: Service classes, domain models, business rules

### Infrastructure Layer
- **Location**: `src/infrastructure/`
- **Purpose**: External service integrations
- **Components**: RAG implementations, repositories, blob storage, LLM providers

## Component Diagram

```
React Frontend
    |
    | HTTP/WebSocket
    v
Flask Application
    |
    +-- API Routes --------> Services -------> Repositories --> PostgreSQL
    |                           |                    |
    |                           +-------------------> BlobStorage --> S3
    |                           |
    |                           +-------------------> RAG Engine --> Qdrant
    |
    +-- WebSocket ---------> ChatService ------> RAG + LLM --> Response Stream
    |
    +-- Middleware (Security, Logging, Rate Limiting)
```

## Data Flow

### Document Upload (Detailed Workflow)
```
1. User uploads file via React Frontend.
2. Flask Backend receives multipart/form-data.
3. DocumentService extracts text and calculates content hash.
4. Server stores file in BlobStorage (e.g., MinIO/S3).
5. Server creates Document record in PostgreSQL with "pending" status.
6. Server publishes a `document.uploaded` event to RabbitMQ (containing document_id, user_id, workspace_id, etc.).
7. An Ingestion Worker (or a chain of workers: parser, chunker, embedder, indexer) consumes the `document.uploaded` event.
8. The worker downloads the file, processes it (parses, chunks, generates embeddings), and stores vectors/graphs in Qdrant/Neo4j.
9. During processing, the worker emits granular status update events (e.g., `document.processing.chunked`, `document.processing.embedded`, `document.processing.ready`) to RabbitMQ.
10. The Server receives these status update events.
11. The Server updates the Document's `processing_status` in PostgreSQL.
12. The Server emits real-time status updates to the React Frontend via WebSockets (Socket.IO).
13. If any step fails, the worker emits a `document.processing.failed` event, and the Server updates the Document status accordingly, notifying the client.
14. Upon `document.processing.ready`, the document is fully integrated into the RAG system and available for querying.
```

### Chat Query (Streaming) (Detailed Workflow)
```
1. User sends message via React Frontend's WebSocket.
2. ChatService in Flask Backend receives the message.
3. ChatService retrieves/creates ChatSession and stores User's ChatMessage in PostgreSQL.
4. ChatService consults RAG configuration for the active workspace.
5. ChatService (or a dedicated RAG worker) performs retrieval:
    a. Queries Vector Store (Qdrant) with user's message embedding.
    b. (Future) Queries Graph Store (Neo4j) for entities/relations.
    c. Retrieves relevant document chunks/nodes (context).
6. **RAG Enhancement Prompt**: If no relevant context is retrieved from the workspace's documents:
    a. The system prompts the user with options: "Upload a Document", "Intelligently Fetch from Wikipedia", or "Continue without additional context".
    b. If "Upload a Document" or "Intelligently Fetch from Wikipedia" is chosen, the chat is paused, and a RAG enhancement job (document ingestion or Wikipedia fetch) is initiated.
    c. Status updates for these enhancement jobs are sent via WebSockets and displayed in the client's "Documents" column.
    d. Once the enhancement job completes and the new context is integrated into the RAG system, the original user query is automatically retried.
    e. If "Continue without additional context" is chosen, the query proceeds to the LLM without further RAG augmentation.
7. ChatService constructs a prompt for the LLM, incorporating conversation history and retrieved context.
8. ChatService interacts with the LLM Provider (Ollama, OpenAI) to get a streaming response.
9. As LLM response tokens are received, the Server emits `chat.chunk` events to the React Frontend via WebSockets.
10. The React Frontend displays tokens in real-time.
11. Upon LLM response completion, ChatService stores the Assistant's full ChatMessage in PostgreSQL.
12. ChatService emits a `chat.complete` event to the React Frontend via WebSockets.
13. If a workspace has documents undergoing processing, chat functionality for that workspace is locked, and chat queries are disabled until all documents are processed.
```

### Workspace Deletion (Detailed Workflow)
```
1. User initiates workspace deletion from the React Frontend.
2. The client immediately updates the workspace's status to 'deleting' in the UI.
3. All interactive elements associated with this workspace (chat input, document uploads, edit buttons) are disabled.
4. The client sends a request to the Flask Backend to delete the workspace.
5. The Flask Backend initiates an asynchronous deletion process, removing the workspace's associated RAG system resources (e.g., Qdrant collection, Neo4j graph) and database records.
6. During this process, the backend sends granular status updates (events) via WebSockets to the client, indicating progress or any errors.
7. The client updates the workspace's status in real-time based on these events.
8. Once the backend confirms the complete deletion (e.g., by sending a final 'ready' status for the workspace being deleted, which is then interpreted by the client to mean full deletion), the workspace is permanently removed from the client's UI, and the user is navigated away (e.g., to the main workspaces list).
9. If deletion fails, the workspace status is updated to 'failed', and an error message is displayed.
```

### RAG Pipeline
```
Documents -> Chunker -> Chunks -> Embedding Model -> Vectors -> Vector Store

Query -> Embedding Model -> Query Vector -> Similarity Search -> Top-K Chunks
     -> LLM Generator with Context -> Answer
```

## Technology Stack

**Backend**:
- Flask 3.1+ with Flask-SocketIO
- PostgreSQL 16 with psycopg2
- Qdrant (vector database)
- Ollama (local LLM)

**Frontend**:
- React 19 + TypeScript + Vite
- TailwindCSS
- Redux Toolkit + React Query
- Socket.IO Client

**Infrastructure**:
- Docker + Docker Compose
- GitHub Actions
- Poetry (Python deps)
- Bun (JS runtime)

## Design Patterns

### Factory Pattern
Creates RAG instances with pluggable components:
```python
rag = create_rag(
    rag_type="vector",
    chunking_strategy="sentence",
    embedding_type="ollama",
    vector_store_type="qdrant"
)
```

### Repository Pattern
Abstracts data access with interfaces:
```python
class DocumentRepository(ABC):
    @abstractmethod
    def create(self, document: Document) -> Document: pass

    @abstractmethod
    def find_by_id(self, doc_id: int) -> Document | None: pass
```

### Dependency Injection
Components receive dependencies via constructor:
```python
class VectorRag(Rag):
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        chunker: Chunker
    ):
        # Dependencies injected, not instantiated
```

### Service Layer
Encapsulates business logic:
```python
class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        blob_storage: BlobStorage,
        rag: Rag
    ):
        # All dependencies injected
```

## Integration Points

### Vector Database (Qdrant)
- **Interface**: `VectorStore`
- **Operations**: add(), search(), delete(), clear()
- **Implementations**: QdrantVectorStore, InMemoryVectorStore

### LLM Providers
- **Interface**: `LlmProvider`
- **Implementations**: OllamaProvider, OpenAIProvider, ClaudeProvider, HuggingFaceProvider
- **Operations**: chat(), chat_stream()

### Embedding Models
- **Interface**: `EmbeddingModel`
- **Implementations**: OllamaEmbeddings, OpenAIEmbeddings, SentenceTransformerEmbeddings
- **Operations**: embed(), get_dimension()

### Blob Storage
- **Interface**: `BlobStorage`
- **Implementations**: S3BlobStorage, FileSystemBlobStorage, InMemoryBlobStorage
- **Operations**: upload_file(), download_file(), delete_file()

### Database (PostgreSQL)
- Repository classes for each domain
- User, document, and chat session management
- Raw SQL with psycopg2 and manual migrations

## Security

- **Authentication**: JWT-based (planned), session management
- **Authorization**: User-scoped access, session ownership validation
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, CSP, CORS
- **Input Validation**: Request size limits, path traversal prevention
- **Rate Limiting**: Per-IP limits with configurable thresholds

## Performance

- **Caching**: Vector embeddings in Qdrant
- **Streaming**: Token-by-token LLM responses for reduced latency
- **Batch Processing**: Batch embeddings and vector insertion
- **Connection Pooling**: Database and HTTP connection reuse

## Development Environment

```bash
# Start all services
docker compose up

# Services:
# - PostgreSQL: localhost:5432
# - Qdrant: localhost:6333 (UI: 6334)
# - Ollama: localhost:11434
# - Backend API: localhost:8000
# - Frontend: localhost:5173
```

## Testing Strategy

**Unit Tests** (`tests/unit/`):
- Test components in isolation with dummy implementations
- No external dependencies, fast execution
- Real objects instead of mocks

**Integration Tests** (`tests/integration/`):
- Test component interactions with testcontainers
- Real databases (Qdrant, PostgreSQL) in Docker
- Clean slate per test

See CLAUDE.md for detailed testing philosophy.

## Future Architecture

- **Graph RAG**: Neo4j database with Leiden clustering
- **Hybrid Search**: Combined vector + graph retrieval
- **Scalability**: Message queues (Celery + Redis), caching layer, load balancing
- **Monitoring**: Structured logging, metrics, health checks
- **Deployment**: Kubernetes, managed services, auto-scaling

## Additional Resources

- [CLAUDE.md](../CLAUDE.md) - Detailed design principles
- [Contributing](contributing.md) - Development guidelines
- [Docker Guide](docker.md) - Container setup
- [API Documentation](../packages/server/docs/api.md)
- [Client User Flows and API Interactions](client-user-flows.md) - Detailed client-side user flows and API interactions.
