# Architecture Documentation

Comprehensive overview of the InsightHub dual RAG system architecture.

## System Overview

InsightHub compares Vector RAG and Graph RAG for academic paper analysis. The system uses clean architecture with clear separation of concerns.

**Core Components**:
1. React Frontend - Document management and chat interface
2. Flask Backend - REST API and WebSocket endpoints
3. RAG Engine - Pluggable retrieval/generation components
4. Vector Database - Qdrant for similarity search
5. PostgreSQL - Application data and chat history
6. LLM Providers - Ollama, OpenAI, Claude, HuggingFace

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

### Document Upload
```
1. User uploads file
2. Flask receives multipart/form-data
3. DocumentService extracts text
4. Store file in BlobStorage
5. Create Document record in PostgreSQL
6. RAG Engine chunks text
7. Generate embeddings
8. Store vectors in Qdrant
9. Return success response
```

### Chat Query (Streaming)
```
1. User sends message via WebSocket
2. ChatService stores user message
3. RAG retrieves relevant chunks from Qdrant
4. Build context from chunks
5. LLM streams response tokens
6. Emit 'chat_chunk' events to frontend
7. Store complete response in PostgreSQL
8. Emit 'chat_complete' event
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
