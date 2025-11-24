# **Project Roadmap / Todo**

## 0. High-Level Goal

Build a configurable RAG platform where users create **Workspaces**, upload documents, configure RAG settings, and start chat sessions that operate over those documents.

System includes:

* Client (React)
* Server (API + RAG orchestration)
* Workers (document processing, retrieval, background tasks)
* CLI
* Shared code libraries
* Containerized deployment (Docker, Swarm, K8s-ready)
* Strong testing, CI, and code quality practices

---

## Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Server (Flask) | Functional | REST API, WebSocket, RAG pipeline working |
| Client (React) | Functional | Chat UI, document management working |
| Workers | Scaffolded | 7 workers created, need implementation |
| Shared Library | Functional | Types, interfaces, events defined |
| CLI | Scaffolded | Basic structure, needs implementation |
| Docker | Complete | Dev, prod, ELK compose files working |
| Vector RAG | Complete | Qdrant integration working |
| Graph RAG | Not Started | Neo4j integration pending |

---

# **1. Workspaces & RAG System**

## 1.1 Workspace Architecture

### *Status: In Progress*

- [x] Define workspace data model
- [x] Define document data model
- [x] Define RAG config data model
- [x] Define chat session data model
- [ ] Implement workspace CRUD API
- [ ] Implement workspace-scoped document storage
- [ ] Implement workspace-level RAG configuration
- [ ] Implement workspace isolation

### *Data Model*

* **Workspace** `1:N` Documents
* **Workspace** `1:1` RAG Config
* **Workspace** `1:N` Chat Sessions

### *Entities*

* **Workspace:** id, name, description, user_id, timestamps
* **Document:** id, workspace_id, filename, file_path, content_type, status, metadata, timestamps
* **RAG Config:** id, workspace_id (unique), rag_type, chunking_strategy, embedding_model, embedding_dim, top_k, timestamps
* **Chat Session:** id, workspace_id, title, timestamps
* **Chat Message:** id, session_id, role, content, metadata, timestamp

### *API Requirements*

- [ ] Workspaces: create, update, delete, list
- [ ] Documents: upload, delete, list, status
- [ ] RAG Config: create, update, validate, retrieve
- [ ] Chat Sessions: create, delete, list, fetch history
- [ ] RAG operations: load workspace config, load document embeddings, run retrieval + LLM response

### *DB Schema*

- [x] PostgreSQL schema defined
- [x] Foreign keys and cascading deletes
- [x] Proper indexing

---

# **2. Client (React)**

## 2.1 Current State

- [x] React 19 + TypeScript + Vite setup
- [x] TailwindCSS styling
- [x] Redux Toolkit state management
- [x] Socket.IO real-time chat
- [x] Feature-based folder structure

## 2.2 Storybook

- [x] Storybook configured
- [ ] Story for each main component
- [ ] Document component variants

## 2.3 E2E Tests

- [x] Playwright tests (319 passing)
- [ ] Consider Cypress migration
- [ ] Cover main workflows:
  - [ ] Sign up / sign in
  - [ ] Change background/theme
  - [ ] Create workspace
  - [ ] Create chat
  - [ ] Upload/delete documents
  - [ ] Delete workspace/chat
  - [ ] Chat with bot

## 2.4 UI/UX Features

- [x] Chat interface
- [x] Document manager
- [x] Theme system (light/dark)
- [ ] Workspaces UI (selection, management)
- [ ] RAG Config UI (global + workspace-level)
- [ ] Settings & Preferences page
- [ ] Document upload status indicators
- [ ] Source citations display

## 2.5 Folder Structure

Current structure follows feature-based architecture:
```
src/features/<feature>/{components/hooks/api/...}
```

- [x] Auth feature module
- [x] Chat feature module
- [x] Documents feature module
- [ ] Workspaces feature module
- [ ] Settings feature module

---

# **3. Server**

## 3.1 Current State

- [x] Flask + SQLAlchemy setup
- [x] Clean architecture (domains/infrastructure)
- [x] Socket.IO integration
- [x] Multiple LLM providers (Ollama, OpenAI, Claude, HuggingFace)
- [x] Qdrant vector store integration
- [x] MinIO/S3 blob storage

## 3.2 Endpoints & Services

- [x] Health check endpoints
- [x] Chat endpoints + WebSocket
- [x] Document endpoints
- [x] Authentication endpoints
- [ ] Workspace CRUD endpoints
- [ ] RAG configuration endpoints
- [ ] Preferences endpoints
- [ ] Worker coordination (RabbitMQ publisher)

## 3.3 Stateless Design

- [x] No local file state
- [x] PostgreSQL for persistence
- [x] MinIO for blob storage
- [ ] Redis integration for caching
- [ ] Session storage in Redis

## 3.4 Cache Implementation

- [ ] Redis for embeddings cache
- [ ] Redis for chat history cache
- [ ] Redis for rate limiting
- [ ] Connection pooling

## 3.5 Security

- [x] Security middleware (headers, CORS)
- [x] Input validation
- [x] Rate limiting middleware
- [ ] JWT authentication (currently session-based)
- [ ] Permission enforcement per workspace
- [ ] RCE-safe document processing

---

# **4. Workers**

## 4.1 Current State

Workers scaffolded in `packages/workers/`:
- `retriever/` - External content fetching
- `parser/` - Document text extraction
- `chucker/` - Text chunking
- `embedder/` - Vector generation
- `indexer/` - Qdrant storage
- `connector/` - Graph construction
- `enricher/` - Metadata enrichment

## 4.2 Implementation Status

| Worker | Status | Priority |
|--------|--------|----------|
| Parser | Scaffolded | High |
| Chunker | Scaffolded | High |
| Embedder | Scaffolded | High |
| Indexer | Scaffolded | High |
| Connector | Scaffolded | Medium |
| Enricher | Scaffolded | Low |
| Retriever | Scaffolded | Medium |

## 4.3 Tasks

- [ ] Implement base worker class with RabbitMQ consumer
- [ ] Implement parser worker (PDF, DOCX, HTML, TXT)
- [ ] Implement chunker worker (sentence, paragraph strategies)
- [ ] Implement embedder worker (Ollama embeddings)
- [ ] Implement indexer worker (Qdrant upsert)
- [ ] Implement connector worker (Neo4j graph building)
- [ ] Implement enricher worker (metadata, summaries)
- [ ] Implement retriever worker (Wikipedia, URL fetching)
- [ ] Add health checks to all workers
- [ ] Add retry logic and dead letter queues

## 4.4 Event Schema

| Event | Producer | Consumer |
|-------|----------|----------|
| `document.uploaded` | Server | Parser |
| `document.parsed` | Parser | Chunker |
| `document.chunked` | Chunker | Embedder |
| `embedding.created` | Embedder | Indexer, Connector |
| `document.indexed` | Indexer | Enricher |
| `graph.updated` | Connector | Enricher |
| `document.enriched` | Enricher | Server |

---

# **5. CLI**

## 5.1 Current State

- [x] Package scaffolded at `packages/cli/`
- [ ] Core implementation

## 5.2 Goals

* TypeScript-based
* Uses shared codebase
* Feature parity with client core features
* Clean commands, good UX
* Test coverage

## 5.3 Tasks

- [ ] Implement auth commands (login, logout, whoami)
- [ ] Implement workspace commands (list, create, delete, select)
- [ ] Implement document commands (upload, list, delete, status)
- [ ] Implement chat commands (interactive chat mode)
- [ ] Implement config commands (view, set)
- [ ] Add shell completions
- [ ] Add CI for CLI
- [ ] Share code between client/server/workers

---

# **6. DevOps / Deployment**

## 6.1 Docker Status

- [x] `docker-compose.yml` - Infrastructure services
- [x] `docker-compose.dev.yml` - Development server/client
- [x] `docker-compose.prod.yml` - Production builds
- [x] `docker-compose.elk.yml` - ELK monitoring
- [ ] `docker-compose.workers.yml` - All workers

## 6.2 Environment & Configuration

- [x] Basic `.env` support
- [ ] Environment layering (.env.local, .env.test, .env.production)
- [ ] Schema validation (Pydantic for Python)
- [ ] Shared config package
- [ ] Worker-specific configs

## 6.3 CI/CD

- [x] GitHub Actions basic setup
- [ ] Trivy security scanning
- [ ] Automated testing in CI
- [ ] Docker image building in CI
- [ ] Automated deployments

## 6.4 Orchestration Readiness

- [x] Docker Compose
- [ ] Docker Swarm configs
- [ ] Kubernetes manifests
- [ ] Health check endpoints for all services

---

# **7. Documentation**

## 7.1 Completed

- [x] Main README.md
- [x] Architecture documentation
- [x] Project structure documentation
- [x] Testing guide
- [x] Docker setup guide
- [x] RAG architecture docs (Vector + Graph)
- [x] Planning documents (requirements, HLD, LLD)

## 7.2 Needed

- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide/manual
- [ ] Developer onboarding guide
- [ ] Worker implementation guide
- [ ] Deployment guide (Swarm/K8s)

---

# **8. Testing**

## 8.1 Current Coverage

| Package | Unit Tests | Integration Tests | E2E Tests |
|---------|-----------|------------------|-----------|
| Server | Partial | Partial | No |
| Client | Yes (319) | No | Yes (Playwright) |
| Shared | Yes | Yes | N/A |
| Workers | No | No | No |
| CLI | No | No | No |

## 8.2 Tasks

- [x] Client unit tests with Vitest
- [x] Client E2E tests with Playwright
- [x] Shared library tests
- [ ] Server integration tests with testcontainers
- [ ] Worker unit tests
- [ ] API tests (Bruno collection fixes)
- [ ] Performance/load tests

---

# **9. Code Quality**

## 9.1 Current State

- [x] Python: Black, isort, Ruff, mypy
- [x] TypeScript: Prettier, ESLint
- [x] Pre-commit hooks
- [x] CI quality checks

## 9.2 Tasks

- [ ] Clean up type definitions (shared vs local)
- [ ] Remove code duplication
- [ ] Ensure strong validation everywhere
- [ ] Add type coverage metrics

---

# **10. Milestones**

### Phase 1: Core Platform (Current)

- [x] Server REST API working
- [x] Client chat interface working
- [x] Vector RAG pipeline working
- [x] Docker development setup
- [x] Basic authentication
- [ ] Workspace management
- [ ] Document status tracking

### Phase 2: Workers & Scalability

- [ ] Implement all workers
- [ ] RabbitMQ event flow working
- [ ] Redis caching layer
- [ ] Horizontal scaling tested

### Phase 3: Graph RAG

- [ ] Neo4j integration
- [ ] Entity extraction worker
- [ ] Graph retrieval implementation
- [ ] Hybrid RAG mode

### Phase 4: Production Ready

- [ ] CLI feature complete
- [ ] Full test coverage
- [ ] Security audit passed
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Kubernetes deployment

---

# **11. Quick Reference**

## Key Commands

```bash
# Development
task up-infra          # Start infrastructure
task up-dev            # Start dev server/client
task check             # Run all quality checks

# Testing
cd packages/client && task test     # Client tests
cd packages/server && task test     # Server tests

# Production
task build && task up  # Build and deploy production
```

## Port Reference

| Service | Port |
|---------|------|
| Client (dev) | 3000 |
| Server (dev) | 5000 |
| PostgreSQL | 5432 |
| Qdrant | 6333 |
| RabbitMQ | 5672 |
| Redis | 6379 |
| MinIO | 9000 |
| Kibana | 5601 |
