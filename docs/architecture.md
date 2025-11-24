# Architecture Documentation

Comprehensive overview of the InsightHub dual RAG system architecture with clean design principles and modern technology stack.

## System Overview

InsightHub is a comprehensive dual RAG (Retrieval-Augmented Generation) system that provides an interactive platform for academic research paper analysis. The system compares Vector RAG and Graph RAG approaches while maintaining clean architecture principles for scalability and maintainability.

### Core Components

1. **React Frontend** - Modern, responsive user interface with real-time updates
2. **Flask Backend** - REST API and WebSocket endpoints with clean architecture
3. **RAG Engine** - Pluggable retrieval/generation components with dual implementations
4. **Vector Database** - Qdrant for high-performance similarity search
5. **Graph Database** - Neo4j for entity-relationship analysis (planned)
6. **PostgreSQL** - Centralized storage for application data and user management
7. **Message Queue** - RabbitMQ for asynchronous document processing
8. **LLM Providers** - Multiple integrations (Ollama, OpenAI, Claude, HuggingFace)

## Architecture Layers

```
+-------------------------------------------------------------+
|                    Presentation Layer                      |
|  (API Routes + WebSocket Handlers + CLI Interface)        |
+-------------------------------------------------------------+
|                      Domain Layer                          |
|     (Business Logic Services + Domain Models)              |
+-------------------------------------------------------------+
|                 Infrastructure Layer                        |
|  (RAG Engine + Database + Storage + LLM Providers)      |
+-------------------------------------------------------------+
```

### Presentation Layer

**Location**: `src/domains/*/routes.py`, `src/domains/*/socket_handlers.py`, `packages/cli/src/`

**Purpose**: Handle HTTP/WebSocket requests and CLI commands

**Components**:
- Flask routes for REST API endpoints
- Socket.IO handlers for real-time communication
- CLI commands for terminal access
- Request validation and response formatting
- Authentication middleware

### Domain Layer

**Location**: `src/domains/*/service.py`, `src/domains/*/models.py`

**Purpose**: Business logic and domain models

**Components**:
- Service classes for business logic
- Domain models and entities
- Business rules and validation
- Use case implementations
- Domain-specific exceptions

### Infrastructure Layer

**Location**: `src/infrastructure/`, `packages/workers/`

**Purpose**: External service integrations

**Components**:
- RAG implementations and components
- Database repositories and connections
- Blob storage integrations
- LLM provider clients
- Message queue handlers
- External API clients

## Component Diagram

```
+-----------------+    HTTP/WebSocket    +-----------------+
|  React Client  | <--------------------> |  Flask Server  |
|                |                     |                 |
| - Workspaces   |                     | - API Routes   |
| - Chat UI      |                     | - WebSocket    |
| - Document Mgmt|                     | - Auth         |
+-----------------+                     +-----------------+
         |                                       |
         |                                       |
    WebSocket                               REST API
         |                                       |
         v                                       v
+-----------------+                     +-----------------+
|   PostgreSQL   | <--------------------> |  RAG Engine    |
|                |                     |                 |
| - Users        |                     | - Vector RAG   |
| - Workspaces   |                     | - Graph RAG    |
| - Chat History |                     | - LLM Providers|
+-----------------+                     +-----------------+
         |                                       |
         |                                       |
    Database                               RAG Operations
         |                                       |
         v                                       v
+-----------------+                     +-----------------+
|     Qdrant     | <--------------------> |   Ollama LLM   |
|                |                     |                 |
| - Vector Store |                     | - Local Models |
| - Similarity  |                     | - Embeddings   |
| - Metadata    |                     | - Generation   |
+-----------------+                     +-----------------+
```

## Data Flow

### Document Upload Workflow

```
1. User uploads file via React Frontend
   |
2. Flask Backend receives multipart/form-data
   |
3. DocumentService validates and processes file
   |
4. File stored in BlobStorage (MinIO/S3)
   |
5. Document record created in PostgreSQL with "pending" status
   |
6. DocumentUploadedEvent published to RabbitMQ
   |
7. Parser Worker consumes event, extracts text
   |
8. Chunker Worker processes text into chunks
   |
9. Embedder Worker generates vector embeddings
   |
10. Indexer Worker stores vectors in Qdrant
   |
11. Status updates sent via WebSocket throughout pipeline
   |
12. Final "ready" status when complete
```

### Chat Query Workflow

```
1. User sends message via React Frontend WebSocket
   |
2. ChatService receives message with session context
   |
3. User message stored in PostgreSQL
   |
4. RAG configuration retrieved for active workspace
   |
5. Query embedding generated using configured model
   |
6. Similarity search performed in Qdrant
   |
7. Top-K relevant chunks retrieved
   |
8. Context-enhanced prompt sent to LLM
   |
9. Streaming response received token-by-token
   |
10. Tokens broadcasted via WebSocket to client
   |
11. Full response stored in PostgreSQL
   |
12. Completion event sent to client
```

### Workspace Provisioning Workflow

```
1. User creates workspace via React Frontend
   |
2. WorkspaceService validates configuration
   |
3. Workspace record created with "provisioning" status
   |
4. RAG configuration stored in PostgreSQL
   |
5. WorkspaceProvisioningEvent published to RabbitMQ
   |
6. Orchestrator Worker consumes event
   |
7. Qdrant collection created for workspace
   |
8. RAG system initialized with configuration
   |
9. Status updates sent via WebSocket
   |
10. Workspace status updated to "ready"
```

## RAG System Architecture

### Vector RAG Implementation

**Location**: `src/infrastructure/rag/vector_rag.py`

**Components**:
- **Chunker**: Text splitting strategies (character, sentence, word)
- **Embedding Model**: Vector generation (Ollama, OpenAI, Sentence Transformers)
- **Vector Store**: Similarity search and storage (Qdrant)
- **Retriever**: Top-K relevant document retrieval
- **LLM Generator**: Context-enhanced response generation

**Pipeline**:
```
Documents -> Chunker -> Chunks -> Embedding Model -> Vectors -> Vector Store
Query -> Embedding Model -> Query Vector -> Similarity Search -> Top-K Chunks
Context -> LLM Generator -> Streaming Response
```

### Graph RAG Implementation (Planned)

**Location**: `src/infrastructure/rag/graph_rag.py` (future implementation)

**Components**:
- **Entity Extractor**: LLM-based entity extraction
- **Relation Extractor**: Relationship identification
- **Graph Builder**: Neo4j graph construction
- **Community Detector**: Leiden clustering algorithm
- **Graph Retriever**: Graph traversal for context

**Pipeline**:
```
Documents -> Entity Extraction -> Relation Extraction -> Graph Builder
Graph -> Community Detection -> Graph Retriever -> Context
Context -> LLM Generator -> Streaming Response
```

## Technology Stack

### Backend Technologies

**Core Framework**:
- **Python 3.11+** with modern type hints
- **Flask 3.0+** as web framework
- **Flask-SocketIO** for WebSocket support
- **Flask-JWT-Extended** for authentication

**Database & Storage**:
- **PostgreSQL 16** for primary data storage
- **Qdrant** for vector storage and similarity search
- **MinIO/S3** for blob storage
- **RabbitMQ** for message queuing

**AI & ML**:
- **Ollama** for local LLM inference
- **OpenAI** API integration
- **Anthropic Claude** API integration
- **Sentence Transformers** for embeddings
- **PyPDF** for document parsing

### Frontend Technologies

**Core Framework**:
- **React 19** with TypeScript
- **Vite** for development and building
- **TailwindCSS** for styling

**State Management**:
- **Redux Toolkit** for global state
- **React Query** for server state
- **Local Storage** for persistence

**Communication**:
- **Socket.IO Client** for real-time communication
- **Axios** for REST API calls

### Infrastructure Technologies

**Containerization**:
- **Docker** & **Docker Compose** for orchestration
- **Multi-stage builds** for optimization
- **Health checks** for monitoring

**Monitoring**:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Structured logging** with correlation IDs
- **Health check endpoints**

**Development Tools**:
- **Poetry** for Python dependency management
- **Bun** for JavaScript runtime
- **Task** for task automation

## Design Patterns

### Factory Pattern

Creates RAG instances with pluggable components:

```python
from src.infrastructure.rag.factory import create_rag

rag = create_rag(
    rag_type="vector",
    chunking_strategy="sentence",
    embedding_type="ollama",
    vector_store_type="qdrant",
    chunk_size=1000,
    chunk_overlap=200,
    top_k=8
)
```

### Repository Pattern

Abstracts data access with clean interfaces:

```python
class DocumentRepository(ABC):
    @abstractmethod
    def create(self, document: Document) -> Document: pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Document | None: pass

    @abstractmethod
    def find_by_workspace(self, workspace_id: str) -> list[Document]: pass
```

### Service Layer Pattern

Encapsulates business logic with dependency injection:

```python
class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        blob_storage: BlobStorage,
        rag: Rag,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.blob_storage = blob_storage
        self.rag = rag
        self.event_publisher = event_publisher
```

### Observer Pattern

Real-time status updates via WebSocket events:

```python
class StatusNotifier:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
    
    def notify_document_status(self, document_id: str, status: str):
        self.socketio.emit('document_status', {
            'document_id': document_id,
            'status': status
        })
```

## Security Architecture

### Authentication & Authorization

**JWT-Based Authentication**:
- Secure token generation and validation
- Token expiration and refresh
- Session management

**Authorization**:
- User-scoped resource access
- Workspace ownership validation
- API endpoint protection

### Security Measures

**Input Validation**:
- Request size limits
- Path traversal prevention
- SQL injection protection
- XSS prevention

**Security Headers**:
- X-Frame-Options
- X-Content-Type-Options
- Content Security Policy
- CORS configuration

**Rate Limiting**:
- Per-IP rate limits
- Endpoint-specific throttling
- Configurable thresholds

## Performance Architecture

### Caching Strategy

**Multi-Level Caching**:
- Vector embeddings cached in Qdrant
- Database connection pooling
- HTTP connection reuse
- Static asset caching

### Optimization Techniques

**Batch Processing**:
- Batch embeddings generation
- Bulk vector insertion
- Parallel document processing

**Streaming**:
- Token-by-token LLM responses
- Real-time status updates
- Progressive document processing

### Scalability Design

**Horizontal Scaling**:
- Stateless server design
- Load balancer ready
- Microservice architecture

**Resource Management**:
- Connection pooling
- Memory-efficient processing
- Graceful degradation

## Monitoring & Observability

### Logging Architecture

**Structured Logging**:
- JSON log format
- Correlation ID tracking
- Request/response logging
- Error stack traces

**Log Levels**:
- DEBUG: Detailed debugging information
- INFO: General information messages
- WARNING: Warning conditions
- ERROR: Error conditions
- CRITICAL: Critical errors

### Health Monitoring

**Health Check Endpoints**:
```bash
GET /health              # Basic health check
GET /health/heartbeat    # Detailed health status
GET /health/database     # Database connectivity
GET /health/queue        # Message queue status
GET /health/rag          # RAG system status
```

**Metrics Collection**:
- Request rate and latency
- Error rates by endpoint
- Database query performance
- RAG system statistics
- Resource utilization

### ELK Integration

**Log Pipeline**:
```
Application Logs -> Filebeat -> Logstash -> Elasticsearch -> Kibana
```

**Dashboard Features**:
- Real-time log streaming
- Error rate monitoring
- Performance metrics
- Custom alerts

## Deployment Architecture

### Container Strategy

**Multi-Stage Builds**:
- Development stage with hot reload
- Production stage with optimizations
- Minimal runtime images
- Security scanning

**Service Orchestration**:
- Docker Compose for local development
- Production-ready configurations
- Health checks and restarts
- Volume management

### Environment Configuration

**Configuration Hierarchy**:
1. Environment variables (highest priority)
2. Configuration files
3. Default values (lowest priority)

**Environment-Specific Settings**:
- Development: Hot reload, debug logging
- Production: Optimized builds, security headers
- Testing: In-memory services, mock data

## Integration Points

### External APIs

**LLM Providers**:
- Ollama (local inference)
- OpenAI (GPT models)
- Anthropic (Claude models)
- HuggingFace (open models)

**Storage Services**:
- MinIO (S3-compatible)
- AWS S3
- Google Cloud Storage

### Message Queue Integration

**RabbitMQ Events**:
- Document processing events
- Workspace provisioning events
- Chat message events
- Status update events

## Future Architecture

### Graph RAG Enhancement

**Neo4j Integration**:
- Entity-relationship graph construction
- Community detection with Leiden algorithm
- Graph-based context retrieval
- Hybrid vector-graph search

### Advanced Features

**Multi-Modal RAG**:
- Image and video processing
- Cross-modal retrieval
- Multi-modal embeddings

**Distributed Processing**:
- Kubernetes deployment
- Auto-scaling workers
- Load balancing
- Fault tolerance

**AI Enhancements**:
- Advanced chunking strategies
- Intelligent query rewriting
- Context compression
- Personalization

## Architecture Principles

### 1. Clean Architecture

- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each component has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Interface Segregation**: Clients don't depend on unused interfaces

### 2. Domain-Driven Design

- **Ubiquitous Language**: Shared vocabulary across teams
- **Bounded Contexts**: Clear domain boundaries
- **Domain Events**: Event-driven communication
- **Aggregate Roots**: Consistency boundaries

### 3. Microservices Architecture

- **Service Independence**: Each service can be developed and deployed independently
- **Database per Service**: Separate databases for different domains
- **API Gateway**: Single entry point for external clients
- **Service Discovery**: Dynamic service location

### 4. Event-Driven Architecture

- **Loose Coupling**: Services communicate through events
- **Asynchronous Processing**: Non-blocking operations
- **Event Sourcing**: Complete audit trail
- **CQRS**: Command Query Responsibility Segregation

This architecture ensures scalability, maintainability, and extensibility while providing a robust foundation for the InsightHub dual RAG system.