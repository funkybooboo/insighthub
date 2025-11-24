# Requirements Document

## 1. Project Overview

**InsightHub** is a dual RAG (Retrieval-Augmented Generation) system comparing Vector RAG and Graph RAG approaches for academic research paper analysis. The system enables users to upload documents, configure RAG settings, and engage in chat sessions powered by intelligent document retrieval.

## 2. Functional Requirements

### 2.1 Workspace Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-WS-01 | System shall allow users to create, update, and delete workspaces | High | [x] Completed |
| FR-WS-02 | Each workspace shall have its own RAG configuration | High | [x] Completed |
| FR-WS-03 | Workspaces shall support multiple documents and chat sessions | High | [x] Completed |
| FR-WS-04 | System shall enforce workspace isolation between users | High | [x] Completed |

### 2.2 Document Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-DOC-01 | System shall support PDF, DOCX, HTML, and TXT file uploads | High | [x] Completed |
| FR-DOC-02 | System shall parse and extract text from uploaded documents | High | [x] Completed |
| FR-DOC-03 | System shall chunk documents using configurable strategies | High | [x] Completed |
| FR-DOC-04 | System shall generate embeddings for document chunks | High | [x] Completed |
| FR-DOC-05 | System shall store embeddings in vector database | High | [x] Completed |
| FR-DOC-06 | System shall extract entities and relations for graph database | Medium | [WIP] In Progress |
| FR-DOC-07 | System shall support document deletion with cascade cleanup | High | [x] Completed |
| FR-DOC-08 | System shall provide document processing status updates | Medium | [x] Completed |

### 2.3 Chat System

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-CHAT-01 | System shall provide real-time chat interface via WebSocket | High | [x] Completed |
| FR-CHAT-02 | System shall stream LLM responses token-by-token | High | [x] Completed |
| FR-CHAT-03 | System shall persist chat history | High | [x] Completed |
| FR-CHAT-04 | System shall retrieve relevant document chunks for context | High | [x] Completed |
| FR-CHAT-05 | System shall support multiple chat sessions per workspace | Medium | [x] Completed |
| FR-CHAT-06 | System shall provide source citations in responses | Medium | [x] Completed |

### 2.4 RAG Configuration

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-RAG-01 | System shall support Vector RAG retrieval mode | High | [x] Completed |
| FR-RAG-02 | System shall support Graph RAG retrieval mode | Medium | [WIP] In Progress |
| FR-RAG-03 | System shall support Hybrid RAG retrieval mode | Low | [TODO] Planned |
| FR-RAG-04 | System shall allow configuration of embedding models | Medium | [x] Completed |
| FR-RAG-05 | System shall allow configuration of chunking strategies | Medium | [x] Completed |
| FR-RAG-06 | System shall allow configuration of top-k retrieval count | Medium | [x] Completed |

### 2.5 User Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-USER-01 | System shall support user registration and authentication | High | [x] Completed |
| FR-USER-02 | System shall enforce user session management | High | [x] Completed |
| FR-USER-03 | System shall scope data access to authenticated users | High | [x] Completed |
| FR-USER-04 | System shall support user preferences (theme, settings) | Low | [TODO] Planned |

### 2.6 External Knowledge

| ID | Requirement | Priority | Status |
|----|-------------|----------|---------|
| FR-EXT-01 | System shall support Wikipedia content retrieval | Medium | [WIP] In Progress |
| FR-EXT-02 | System shall support URL content fetching | Medium | [TODO] Planned |
| FR-EXT-03 | System shall integrate external content into RAG pipeline | Medium | [WIP] In Progress |

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target | Status |
|----|-------------|--------|---------|
| NFR-PERF-01 | Chat response latency (first token) | < 2 seconds | [x] Achieved |
| NFR-PERF-02 | Document upload processing | < 30 seconds for 10MB file | [x] Achieved |
| NFR-PERF-03 | Vector similarity search | < 100ms for top-10 | [x] Achieved |
| NFR-PERF-04 | Concurrent users supported | 100+ | [WIP] Testing |

### 3.2 Scalability

| ID | Requirement | Description | Status |
|----|-------------|-------------|---------|
| NFR-SCALE-01 | Horizontal scaling | Server and workers shall scale independently | [x] Implemented |
| NFR-SCALE-02 | Stateless processes | Server shall maintain no local state | [x] Implemented |
| NFR-SCALE-03 | Message queue | Workers shall communicate via RabbitMQ | [x] Implemented |
| NFR-SCALE-04 | Container orchestration | System shall be deployable to Docker Swarm/K8s | [x] Implemented |

### 3.3 Security

| ID | Requirement | Description | Status |
|----|-------------|-------------|---------|
| NFR-SEC-01 | Authentication | JWT-based authentication | [x] Implemented |
| NFR-SEC-02 | Authorization | User-scoped data access | [x] Implemented |
| NFR-SEC-03 | Input validation | Sanitize all user inputs | [x] Implemented |
| NFR-SEC-04 | Security headers | CSP, X-Frame-Options, CORS | [x] Implemented |
| NFR-SEC-05 | Rate limiting | Per-IP request limits | [WIP] In Progress |
| NFR-SEC-06 | Secret management | No secrets in Docker images | [x] Implemented |

### 3.4 Reliability

| ID | Requirement | Target | Status |
|----|-------------|--------|---------|
| NFR-REL-01 | System uptime | 99.5% | [WIP] Monitoring |
| NFR-REL-02 | Data durability | No data loss on worker failure | [x] Implemented |
| NFR-REL-03 | Graceful degradation | System operates if optional services unavailable | [x] Implemented |

### 3.5 Maintainability

| ID | Requirement | Description | Status |
|----|-------------|-------------|---------|
| NFR-MAINT-01 | Code quality | Linting, formatting, type checking enforced | [x] Implemented |
| NFR-MAINT-02 | Test coverage | Minimum 80% for critical paths | [WIP] In Progress |
| NFR-MAINT-03 | Documentation | API docs, architecture docs, setup guides | [x] Implemented |
| NFR-MAINT-04 | Logging | Structured logging with ELK integration | [x] Implemented |

## 4. System Constraints

### 4.1 Technology Stack

| Component | Technology | Status |
|-----------|------------|---------|
| Frontend | React 19, TypeScript, Vite, TailwindCSS, Redux | [x] Implemented |
| Backend | Python 3.11, Flask, SQLAlchemy, Socket.IO | [x] Implemented |
| Vector DB | Qdrant | [x] Implemented |
| Graph DB | Neo4j | [x] Implemented |
| Relational DB | PostgreSQL | [x] Implemented |
| Cache | Redis | [x] Implemented |
| Message Queue | RabbitMQ | [x] Implemented |
| Object Storage | Filesystem (local) | [x] Implemented |
| LLM | Ollama (local), OpenAI, Claude, HuggingFace | [x] Implemented |
| Containerization | Docker, Docker Compose | [x] Implemented |
| CI/CD | GitHub Actions | [x] Implemented |

### 4.2 Deployment Environments

- **Development**: [x] Docker Compose with hot-reload
- **Production**: [x] Docker Compose with optimized builds
- **Future**: [TODO] Docker Swarm, Kubernetes

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

- Chat history: [x] Indefinite (user-controlled deletion)
- Documents: [x] Until workspace deletion
- Embeddings: [x] Cascade delete with documents
- Logs: [x] 30-day retention in ELK

## 6. Interface Requirements

### 6.1 User Interfaces

- [x] Web-based React client
- [x] Command-line interface (CLI)
- [TODO] Mobile-responsive design (future)

### 6.2 External Interfaces

- [x] REST API for CRUD operations
- [x] WebSocket for real-time chat
- [x] RabbitMQ for worker communication

## 7. Acceptance Criteria

### 7.1 Minimum Viable Product (MVP)

- [x] User can create workspaces and upload documents
- [x] Documents are processed and indexed for Vector RAG
- [x] User can chat and receive RAG-powered responses
- [x] Responses stream in real-time
- [x] System runs via `docker compose up`

### 7.2 Full Feature Set

- [x] All MVP features
- [ ] Graph RAG implementation with Neo4j
- [ ] Hybrid RAG combining Vector and Graph
- [ ] Wikipedia/URL content retrieval
- [x] CLI with feature parity
- [ ] Comprehensive test coverage
- [x] Production-ready deployment configs

## 8. Implementation Status Summary

### 8.1 Completed Features [x]

**Core Infrastructure:**
- Flask 3.0+ backend with clean architecture
- React 19 frontend with TypeScript and Redux
- PostgreSQL for application data
- Qdrant vector database for VectorRAG
- Neo4j graph database setup
- Redis for caching and session management
- RabbitMQ for background job processing
- Docker Compose orchestration

**VectorRAG Implementation:**
- Document upload and parsing (PDF, DOCX, HTML, TXT)
- Multiple chunking strategies (character, sentence, word)
- Ollama integration for embeddings (nomic-embed-text)
- Vector similarity search with configurable top-k
- Real-time chat with streaming responses
- Source citation and metadata tracking

**Chat System:**
- WebSocket-based real-time communication
- Conversation history persistence
- User authentication with JWT
- Workspace-based organization
- Multi-session support

**Development Tools:**
- Comprehensive testing setup (Pytest, Vitest, Playwright)
- CI/CD with GitHub Actions
- ELK stack for monitoring
- Task-based build system
- Bruno for API testing

### 8.2 In Progress Features [WIP]

**GraphRAG Implementation:**
- Entity extraction using LLMs
- Relationship extraction and graph construction
- Leiden clustering algorithm implementation
- Graph-based retrieval strategies

**External Knowledge:**
- Wikipedia MCP integration
- Dynamic content fetching
- Knowledge graph enrichment

**Performance & Security:**
- Rate limiting implementation
- Load testing for concurrent users
- Security hardening and penetration testing

### 8.3 Planned Features [TODO]

**Advanced RAG:**
- Hybrid Vector + Graph retrieval
- Context-aware chunking
- Query expansion and reformulation
- Multi-modal document support

**User Experience:**
- Advanced search and filtering
- Document visualization
- Analytics and usage metrics
- Mobile-responsive design

**Production Readiness:**
- Comprehensive test coverage (80%+)
- Performance optimization
- Security audit and hardening
- Scalability testing

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| GraphRAG complexity | Medium | High | Incremental implementation, extensive testing |
| Performance at scale | Medium | Medium | Load testing, optimization planning |
| External service dependencies | Low | Medium | Fallback mechanisms, local alternatives |
| Security vulnerabilities | Low | High | Regular audits, security best practices |

### 9.2 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Timeline delays | Medium | Medium | Agile development, feature prioritization |
| Resource constraints | Low | Medium | Cloud deployment options, optimization |
| Integration complexity | Medium | Low | Modular architecture, comprehensive testing |

## 10. Success Metrics

### 10.1 Technical Metrics

- **Performance**: < 2s chat response, < 100ms vector search
- **Reliability**: > 99.5% uptime, zero data loss
- **Scalability**: Support 100+ concurrent users
- **Quality**: > 80% test coverage, zero critical bugs

### 10.2 User Experience Metrics

- **Usability**: Intuitive interface, minimal learning curve
- **Functionality**: All MVP features working correctly
- **Performance**: Responsive UI, fast document processing
- **Reliability**: Consistent behavior, error-free operation

This requirements document serves as the foundation for developing InsightHub and tracking progress toward project completion.