# High-Level Design Document

## 1. System Overview

InsightHub is a dual RAG (Retrieval-Augmented Generation) platform designed to compare Vector RAG and Graph RAG approaches. The system follows clean architecture principles with clear separation between presentation, domain, and infrastructure layers, implemented as a Flask-based monorepo with React frontend.

## 2. Architecture Diagram

```
                                     +-------------------+
                                     |   React Client    |
                                     |  (Web Interface)  |
                                     +--------+----------+
                                              |
                               HTTP/REST      |     WebSocket
                          +------------------+-+------------------+
                          |                                       |
                          v                                       v
               +----------+----------+               +------------+-----------+
               |    Flask Server     |               |    Socket.IO Server    |
               |    (REST API)       |               |    (Real-time Chat)    |
               +----------+----------+               +------------+-----------+
                          |                                       |
                          +-------------------+-------------------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
            +--------+--------+     +---------+--------+     +---------+--------+
            |   PostgreSQL    |     |     RabbitMQ     |     |      Redis       |
            | (Application DB)|     |  (Message Queue) |     |     (Cache)      |
            +-----------------+     +---------+--------+     +------------------+
                                              |
               +------------------------------+------------------------------+
               |              |               |               |              |
               v              v               v               v              v
         +-----+----+  +------+-----+  +------+-----+  +------+-----+  +-----+----+
         | Retriever|  |   Parser   |  |  Chunker   |  | Embedder   |  | Indexer  |
         | Worker   |  |   Worker   |  |   Worker   |  |  Worker    |  | Worker   |
         +----------+  +------------+  +------------+  +------+-----+  +-----+----+
                                                              |              |
                                                              v              v
                                                       +------+-----+  +-----+------+
                                                       | Connector  |  |  Enricher  |
                                                       |  Worker    |  |   Worker   |
                                                       +------+-----+  +------------+
                                                              |
                     +----------------------------------------+
                     |                                        |
                     v                                        v
            +--------+--------+                     +---------+--------+
            |     Qdrant      |                     |      Neo4j       |
            |  (Vector DB)    |                     |   (Graph DB)     |
            +-----------------+                     +------------------+
```

## 3. Component Architecture

### 3.1 Presentation Layer

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| React Client | React 19, TypeScript, Redux, TailwindCSS | User interface, state management, real-time chat |
| CLI | TypeScript, Bun | Command-line interface for system management |
| REST API | Flask 3.0+, Flask-RESTx | HTTP endpoints for CRUD operations |
| WebSocket | Flask-SocketIO | Real-time bidirectional communication |

### 3.2 Domain Layer

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Auth Domain | `server/src/domains/auth/` | JWT authentication and user management |
| Chat Domain | `server/src/domains/chat/` | Chat sessions, messages, and streaming |
| Documents Domain | `server/src/domains/documents/` | Document upload, processing, and management |
| Users Domain | `server/src/domains/users/` | User profiles and workspace management |
| Health Domain | `server/src/domains/health/` | System health checks and monitoring |

### 3.3 Infrastructure Layer

| Component | Location | Responsibility |
|-----------|----------|----------------|
| RAG Engine | `server/src/infrastructure/rag/` | Vector and Graph RAG pipeline implementations |
| Database | `server/src/infrastructure/database/` | PostgreSQL ORM with SQLAlchemy |
| Storage | `server/src/infrastructure/storage/` | File storage (local filesystem) |
| LLM Providers | `server/src/infrastructure/llm/` | Ollama, OpenAI, Anthropic integrations |
| External APIs | `server/src/infrastructure/external/` | Wikipedia and external content fetching |

### 3.4 Worker Layer

| Worker | Responsibility | Input Event | Output Event |
|--------|---------------|-------------|--------------|
| Retriever | Fetch external content | `query.external` | `document.uploaded` |
| Parser | Extract text from files | `document.ingested` | `document.parsed` |
| Chunker | Split text into chunks | `document.parsed` | `document.chunked` |
| Embedder | Generate vector embeddings | `document.chunked` | `embedding.created` |
| Indexer | Store in vector database | `embedding.created` | `document.indexed` |
| Connector | Build knowledge graph | `embedding.created` | `graph.updated` |
| Enricher | Add metadata, summaries | `document.indexed` | `document.enriched` |

## 4. Data Flow

### 4.1 Document Upload Flow

```
1. User uploads document via React Client
2. Client sends multipart/form-data to Flask Server
3. Server stores file in local filesystem
4. Server creates Document record in PostgreSQL
5. Server publishes `document.uploaded` to RabbitMQ
6. Parser Worker consumes event, extracts text
7. Chunker Worker chunks text using configurable strategies
8. Embedder Worker generates embeddings with Ollama
9. Indexer Worker stores in Qdrant vector database
10. Connector Worker builds graph nodes/edges in Neo4j
11. Enricher Worker adds metadata and summaries
12. Server receives completion, updates status
13. Client receives status update via WebSocket
```

### 4.2 Chat Query Flow

```
1. User sends message via WebSocket
2. Server receives and stores user message in PostgreSQL
3. Server encodes query to vector using Ollama embeddings
4. RAG Engine retrieves relevant chunks from Qdrant
5. (Optional) RAG Engine expands context via Neo4j graph traversal
6. Context builder assembles LLM prompt with retrieved context
7. LLM generates response (streaming via Ollama)
8. Server emits `chat_chunk` events to client in real-time
9. Server stores complete response in PostgreSQL
10. Server emits `chat_complete` event with sources and citations
```

## 5. Package Structure

```
insighthub/
+-- packages/
|   +-- shared/           # Shared types and utilities
|   |   +-- python/       # Python shared library
|   |   +-- typescript/   # TypeScript shared types
|   +-- server/           # Flask backend
|   |   +-- src/
|   |   |   +-- domains/              # Business logic by feature
|   |   |   +-- infrastructure/       # External integrations
|   |   |   +-- api.py               # Flask application entry
|   |   +-- tests/                    # Unit and integration tests
|   +-- client/           # React frontend
|   |   +-- src/
|   |   |   +-- components/          # React components
|   |   |   +-- pages/               # Page components
|   |   |   +-- hooks/               # Custom React hooks
|   |   |   +-- services/            # API services
|   |   |   +-- lib/                 # Utilities and configuration
|   +-- workers/          # Background workers
|   |   +-- retriever/    # External content fetching
|   |   +-- parser/       # Document parsing
|   |   +-- chucker/      # Text chunking
|   |   +-- embedder/     # Vector embedding generation
|   |   +-- indexer/      # Vector database indexing
|   |   +-- connector/    # Graph database construction
|   |   +-- enricher/      # Metadata enrichment
|   +-- cli/              # Command-line interface
+-- docs/                 # Documentation
|   +-- planning/         # Design documents
|   +-- project-management/
+-- elk/                  # ELK monitoring configuration
+-- docker-compose*.yml   # Service orchestration
+-- Taskfile.yml          # Build commands and utilities
```

## 6. Technology Decisions

### 6.1 Why This Stack?

| Decision | Rationale |
|----------|-----------|
| Flask over FastAPI | Simpler WebSocket integration with Flask-SocketIO, mature ecosystem |
| Qdrant for vectors | High performance, Docker-friendly, built-in HNSW indexing |
| Neo4j for graphs | Industry standard, Cypher query language, built-in clustering |
| RabbitMQ over Kafka | Simpler operations, sufficient for current document processing scale |
| PostgreSQL | ACID compliance, JSONB support, mature ecosystem, reliable |
| Redux for state | Predictable state management, dev tools, middleware support |
| Docker Compose | Simple multi-container orchestration, development parity |
| Bun for frontend | Fast TypeScript execution, built-in bundler and package manager |

### 6.2 Scalability Strategy

1. **Horizontal Scaling**: Workers scale independently based on queue depth
2. **Stateless Server**: All state in PostgreSQL/Redis, enabling load balancing
3. **Event-Driven**: Async processing via RabbitMQ decouples components
4. **Caching**: Redis for embeddings cache, session cache, rate limiting
5. **Database Scaling**: Connection pooling, read replicas (future enhancement)

## 7. Integration Points

### 7.1 External Services

| Service | Purpose | Integration Method |
|---------|---------|-------------------|
| Ollama | Local LLM inference | HTTP API |
| OpenAI | Cloud LLM | REST API |
| Anthropic Claude | Cloud LLM | REST API |
| Wikipedia | External knowledge | REST API (via MCP) |
| HuggingFace | Models & embeddings | REST API |

### 7.2 Internal Services

| Service | Port | Protocol |
|---------|------|----------|
| React Client | 3000 (dev), 80 (prod) | HTTP |
| Flask Server | 5000 (dev), 8000 (prod) | HTTP/WS |
| PostgreSQL | 5432 | TCP |
| Qdrant | 6333 | HTTP |
| Neo4j | 7687 | Bolt |
| RabbitMQ | 5672 | AMQP |
| Redis | 6379 | TCP |
| Elasticsearch | 9200 | HTTP |
| Kibana | 5601 | HTTP |

## 8. Security Architecture

### 8.1 Authentication Flow

```
1. User submits credentials via React Client
2. Server validates against PostgreSQL using bcrypt
3. Server issues JWT token with user ID and expiration
4. Client stores token securely (httpOnly cookie or localStorage)
5. Client includes token in Authorization header for API requests
6. Server middleware validates JWT token on each protected request
7. Server extracts user context for data scoping and authorization
```

### 8.2 Security Layers

| Layer | Mechanism |
|-------|-----------|
| Transport | HTTPS (production), HTTP (development) |
| Authentication | JWT tokens with RS256 signing |
| Authorization | User-scoped data access, workspace isolation |
| Input Validation | Marshmallow schema validation, XSS protection |
| Rate Limiting | Per-IP and per-user limits via Redis |
| Secrets | Environment variables, Docker secrets |
| CORS | Configurable origins for API access |

## 9. Monitoring and Observability

### 9.1 ELK Stack Integration

- **Filebeat**: Collects container logs from all services
- **Logstash**: Processes and transforms logs with grok patterns
- **Elasticsearch**: Stores and indexes logs for full-text search
- **Kibana**: Visualization dashboards and log analysis

### 9.2 Health Checks

- `/health` endpoint on Flask server with dependency checks
- Docker health checks for all containers
- RabbitMQ queue depth monitoring
- Database connection pool monitoring
- Redis connectivity checks

### 9.3 Application Metrics

- Request/response times and error rates
- Document processing pipeline status and throughput
- Chat query latency and RAG retrieval performance
- Worker queue depths and processing times
- Resource utilization (CPU, memory, disk)

## 10. Deployment Topology

### 10.1 Development

```
docker-compose.yml (infrastructure services)
  + docker-compose.dev.yml (server-dev, client-dev)
  + docker-compose.elk.yml (optional monitoring)
```

### 10.2 Production

```
docker-compose.yml (infrastructure services)
  + docker-compose.prod.yml (server-prod, client-prod)
  + docker-compose.elk.yml (monitoring stack)
```

### 10.3 Full Stack (with Workers)

```
docker-compose.yml (infrastructure)
  + docker-compose.dev.yml / docker-compose.prod.yml
  + docker-compose.workers.yml (all background workers)
  + docker-compose.elk.yml (monitoring and observability)
```

## 11. Clean Architecture Principles

### 11.1 Dependency Flow

```
Outer Layer (Infrastructure) -> Middle Layer (Domain) -> Inner Layer (Entities)
```

- **Entities**: Core business objects with no external dependencies
- **Domain**: Business logic and use cases, depends on Entities
- **Infrastructure**: External concerns (DB, APIs, workers), depends on Domain
- **Presentation**: UI and API layer, depends on Domain

### 11.2 Key Patterns

- **Dependency Injection**: All dependencies injected via constructors
- **Repository Pattern**: Data access abstraction for testability
- **Service Layer**: Business logic encapsulation in domain services
- **Factory Pattern**: RAG engine creation with configurable components
- **Observer Pattern**: WebSocket events for real-time updates

## 12. Testing Strategy

### 12.1 Test Pyramid

- **Unit Tests**: Fast, isolated tests for domain logic and utilities
- **Integration Tests**: Database and external service integration
- **End-to-End Tests**: Full user workflows via browser automation
- **Performance Tests**: Load testing for chat and document processing

### 12.2 Test Tools

- **Python**: Pytest for unit/integration, testcontainers for Docker services
- **TypeScript**: Vitest for unit tests, Playwright for E2E tests
- **API Testing**: Bruno for API collection and contract testing
- **Load Testing**: Artillery for chat performance testing

This high-level design provides the foundation for implementing a scalable, maintainable dual RAG system that can effectively compare Vector and Graph approaches for academic research paper analysis.