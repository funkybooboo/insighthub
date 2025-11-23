# High-Level Design Document

## 1. System Overview

InsightHub is a modular RAG (Retrieval-Augmented Generation) platform designed to compare Vector RAG and Graph RAG approaches. The system follows clean architecture principles with clear separation between presentation, domain, and infrastructure layers.

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
| React Client | React 19, TypeScript, Redux | User interface, state management |
| CLI | TypeScript | Command-line interface |
| REST API | Flask | HTTP endpoints for CRUD operations |
| WebSocket | Socket.IO | Real-time bidirectional communication |

### 3.2 Domain Layer

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Auth Domain | `server/src/domains/auth/` | User authentication and authorization |
| Chat Domain | `server/src/domains/chat/` | Chat sessions and message handling |
| Documents Domain | `server/src/domains/documents/` | Document upload and management |
| Users Domain | `server/src/domains/users/` | User profile and preferences |
| Health Domain | `server/src/domains/health/` | System health checks |

### 3.3 Infrastructure Layer

| Component | Location | Responsibility |
|-----------|----------|----------------|
| RAG Engine | `server/src/infrastructure/rag/` | RAG pipeline implementations |
| LLM Providers | `server/src/infrastructure/llm/` | Multiple LLM integrations |
| Storage | `server/src/infrastructure/storage/` | Blob storage (S3, MinIO) |
| Database | `server/src/infrastructure/database/` | PostgreSQL ORM |
| Messaging | `server/src/infrastructure/messaging/` | RabbitMQ publisher |

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
3. Server stores file in MinIO/S3
4. Server creates Document record in PostgreSQL
5. Server publishes `document.uploaded` to RabbitMQ
6. Parser Worker consumes event, extracts text
7. Chunker Worker chunks text
8. Embedder Worker generates embeddings
9. Indexer Worker stores in Qdrant
10. Connector Worker builds graph nodes/edges in Neo4j
11. Enricher Worker adds metadata
12. Server receives completion, updates status
13. Client receives status update via WebSocket
```

### 4.2 Chat Query Flow

```
1. User sends message via WebSocket
2. Server receives and stores user message
3. Server encodes query to vector
4. RAG Engine retrieves relevant chunks from Qdrant
5. (Optional) RAG Engine expands context via Neo4j
6. Context builder assembles LLM prompt
7. LLM generates response (streaming)
8. Server emits `chat_chunk` events to client
9. Server stores complete response
10. Server emits `chat_complete` event
```

## 5. Package Structure

```
insighthub/
+-- packages/
|   +-- shared/           # Shared types, interfaces, utilities
|   |   +-- python/       # Python shared library
|   +-- server/           # Flask backend
|   |   +-- src/
|   |   |   +-- domains/  # Business logic by feature
|   |   |   +-- infrastructure/  # External integrations
|   |   +-- tests/
|   +-- client/           # React frontend
|   |   +-- src/
|   |   |   +-- features/ # Feature-based components
|   |   |   +-- shared/   # Shared UI components
|   +-- workers/          # Background workers
|   |   +-- retriever/
|   |   +-- parser/
|   |   +-- chucker/
|   |   +-- embedder/
|   |   +-- indexer/
|   |   +-- connector/
|   |   +-- enricher/
|   +-- cli/              # Command-line interface
+-- docs/                 # Documentation
+-- elk/                  # ELK monitoring config
+-- docker-compose*.yml   # Service orchestration
+-- Taskfile.yml          # Build commands
```

## 6. Technology Decisions

### 6.1 Why This Stack?

| Decision | Rationale |
|----------|-----------|
| Flask over FastAPI | Simpler WebSocket integration with Socket.IO |
| Qdrant for vectors | High performance, Docker-friendly, built-in HNSW |
| Neo4j for graphs | Industry standard, Cypher query language |
| RabbitMQ over Kafka | Simpler ops, sufficient for current scale |
| PostgreSQL | ACID compliance, JSONB support, mature ecosystem |
| Redux for state | Predictable state, dev tools, middleware support |
| Docker Compose | Simple multi-container orchestration |

### 6.2 Scalability Strategy

1. **Horizontal Scaling**: Workers scale independently based on queue depth
2. **Stateless Server**: All state in PostgreSQL/Redis, enabling load balancing
3. **Event-Driven**: Async processing via RabbitMQ decouples components
4. **Caching**: Redis for embeddings cache, session cache, rate limiting
5. **Database Scaling**: Connection pooling, read replicas (future)

## 7. Integration Points

### 7.1 External Services

| Service | Purpose | Integration Method |
|---------|---------|-------------------|
| Ollama | Local LLM inference | HTTP API |
| OpenAI | Cloud LLM | REST API |
| Anthropic Claude | Cloud LLM | REST API |
| HuggingFace | Models & embeddings | REST API |
| Wikipedia | External knowledge | REST API (via MCP) |

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
| MinIO | 9000 | HTTP |
| Elasticsearch | 9200 | HTTP |
| Kibana | 5601 | HTTP |

## 8. Security Architecture

### 8.1 Authentication Flow

```
1. User submits credentials
2. Server validates against PostgreSQL
3. Server issues JWT token (or creates session)
4. Client stores token
5. Client includes token in Authorization header
6. Server middleware validates token on each request
7. Server extracts user context for data scoping
```

### 8.2 Security Layers

| Layer | Mechanism |
|-------|-----------|
| Transport | HTTPS (production) |
| Authentication | JWT tokens or session cookies |
| Authorization | User-scoped data access |
| Input Validation | Schema validation, sanitization |
| Rate Limiting | Per-IP limits via middleware |
| Secrets | Environment variables, Docker secrets |

## 9. Monitoring and Observability

### 9.1 ELK Stack Integration

- **Filebeat**: Collects container logs
- **Logstash**: Processes and transforms logs
- **Elasticsearch**: Stores and indexes logs
- **Kibana**: Visualization and dashboards

### 9.2 Health Checks

- `/health` endpoint on server
- Docker health checks for containers
- RabbitMQ queue monitoring
- Database connection checks

## 10. Deployment Topology

### 10.1 Development

```
docker-compose.yml (infrastructure)
  + docker-compose.dev.yml (server-dev, client-dev)
  + docker-compose.elk.yml (optional monitoring)
```

### 10.2 Production

```
docker-compose.yml (infrastructure)
  + docker-compose.prod.yml (server-prod, client-prod)
  + docker-compose.elk.yml (monitoring)
```

### 10.3 Full Stack (with Workers)

```
docker-compose.yml (infrastructure)
  + docker-compose.dev.yml / docker-compose.prod.yml
  + docker-compose.workers.yml (all workers)
  + docker-compose.elk.yml (monitoring)
```
