# Requirements Document

## 1. Project Overview

**InsightHub** is a dual RAG (Retrieval-Augmented Generation) system comparing Vector RAG and Graph RAG approaches for academic research paper analysis. The system enables users to upload documents, configure RAG settings, and engage in chat sessions powered by intelligent document retrieval.

## 2. Functional Requirements

### 2.1 Workspace Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WS-01 | System shall allow users to create, update, and delete workspaces | High |
| FR-WS-02 | Each workspace shall have its own RAG configuration | High |
| FR-WS-03 | Workspaces shall support multiple documents and chat sessions | High |
| FR-WS-04 | System shall enforce workspace isolation between users | High |

### 2.2 Document Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DOC-01 | System shall support PDF, DOCX, HTML, and TXT file uploads | High |
| FR-DOC-02 | System shall parse and extract text from uploaded documents | High |
| FR-DOC-03 | System shall chunk documents using configurable strategies | High |
| FR-DOC-04 | System shall generate embeddings for document chunks | High |
| FR-DOC-05 | System shall store embeddings in vector database | High |
| FR-DOC-06 | System shall extract entities and relations for graph database | Medium |
| FR-DOC-07 | System shall support document deletion with cascade cleanup | High |
| FR-DOC-08 | System shall provide document processing status updates | Medium |

### 2.3 Chat System

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CHAT-01 | System shall provide real-time chat interface via WebSocket | High |
| FR-CHAT-02 | System shall stream LLM responses token-by-token | High |
| FR-CHAT-03 | System shall persist chat history | High |
| FR-CHAT-04 | System shall retrieve relevant document chunks for context | High |
| FR-CHAT-05 | System shall support multiple chat sessions per workspace | Medium |
| FR-CHAT-06 | System shall provide source citations in responses | Medium |

### 2.4 RAG Configuration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RAG-01 | System shall support Vector RAG retrieval mode | High |
| FR-RAG-02 | System shall support Graph RAG retrieval mode | Medium |
| FR-RAG-03 | System shall support Hybrid RAG retrieval mode | Low |
| FR-RAG-04 | System shall allow configuration of embedding models | Medium |
| FR-RAG-05 | System shall allow configuration of chunking strategies | Medium |
| FR-RAG-06 | System shall allow configuration of top-k retrieval count | Medium |

### 2.5 User Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-USER-01 | System shall support user registration and authentication | High |
| FR-USER-02 | System shall enforce user session management | High |
| FR-USER-03 | System shall scope data access to authenticated users | High |
| FR-USER-04 | System shall support user preferences (theme, settings) | Low |

### 2.6 External Knowledge

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EXT-01 | System shall support Wikipedia content retrieval | Medium |
| FR-EXT-02 | System shall support URL content fetching | Medium |
| FR-EXT-03 | System shall integrate external content into RAG pipeline | Medium |

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-01 | Chat response latency (first token) | < 2 seconds |
| NFR-PERF-02 | Document upload processing | < 30 seconds for 10MB file |
| NFR-PERF-03 | Vector similarity search | < 100ms for top-10 |
| NFR-PERF-04 | Concurrent users supported | 100+ |

### 3.2 Scalability

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-SCALE-01 | Horizontal scaling | Server and workers shall scale independently |
| NFR-SCALE-02 | Stateless processes | Server shall maintain no local state |
| NFR-SCALE-03 | Message queue | Workers shall communicate via RabbitMQ |
| NFR-SCALE-04 | Container orchestration | System shall be deployable to Docker Swarm/K8s |

### 3.3 Security

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-SEC-01 | Authentication | JWT-based or session authentication |
| NFR-SEC-02 | Authorization | User-scoped data access |
| NFR-SEC-03 | Input validation | Sanitize all user inputs |
| NFR-SEC-04 | Security headers | CSP, X-Frame-Options, CORS |
| NFR-SEC-05 | Rate limiting | Per-IP request limits |
| NFR-SEC-06 | Secret management | No secrets in Docker images |

### 3.4 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-REL-01 | System uptime | 99.5% |
| NFR-REL-02 | Data durability | No data loss on worker failure |
| NFR-REL-03 | Graceful degradation | System operates if optional services unavailable |

### 3.5 Maintainability

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-MAINT-01 | Code quality | Linting, formatting, type checking enforced |
| NFR-MAINT-02 | Test coverage | Minimum 80% for critical paths |
| NFR-MAINT-03 | Documentation | API docs, architecture docs, setup guides |
| NFR-MAINT-04 | Logging | Structured logging with ELK integration |

## 4. System Constraints

### 4.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 19, TypeScript, Vite, TailwindCSS, Redux |
| Backend | Python 3.11, Flask, SQLAlchemy, Socket.IO |
| Vector DB | Qdrant |
| Graph DB | Neo4j (planned) |
| Relational DB | PostgreSQL |
| Cache | Redis |
| Message Queue | RabbitMQ |
| Object Storage | MinIO/S3 |
| LLM | Ollama (local), OpenAI, Claude, HuggingFace |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |

### 4.2 Deployment Environments

- **Development**: Docker Compose with hot-reload
- **Production**: Docker Compose with optimized builds
- **Future**: Docker Swarm, Kubernetes

## 5. Data Requirements

### 5.1 Data Model

```
Workspace 1:N Document
Workspace 1:1 RAG Config
Workspace 1:N Chat Session
Chat Session 1:N Chat Message
User 1:N Workspace
```

### 5.2 Data Retention

- Chat history: Indefinite (user-controlled deletion)
- Documents: Until workspace deletion
- Embeddings: Cascade delete with documents
- Logs: 30-day retention in ELK

## 6. Interface Requirements

### 6.1 User Interfaces

- Web-based React client
- Command-line interface (CLI)
- Mobile-responsive design (future)

### 6.2 External Interfaces

- REST API for CRUD operations
- WebSocket for real-time chat
- RabbitMQ for worker communication

## 7. Acceptance Criteria

### 7.1 Minimum Viable Product (MVP)

- [ ] User can create workspaces and upload documents
- [ ] Documents are processed and indexed for Vector RAG
- [ ] User can chat and receive RAG-powered responses
- [ ] Responses stream in real-time
- [ ] System runs via `docker compose up`

### 7.2 Full Feature Set

- [ ] All MVP features
- [ ] Graph RAG implementation with Neo4j
- [ ] Hybrid RAG combining Vector and Graph
- [ ] Wikipedia/URL content retrieval
- [ ] CLI with feature parity
- [ ] Comprehensive test coverage
- [ ] Production-ready deployment configs
