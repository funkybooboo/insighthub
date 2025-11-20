# InsightHub - Project Status

**Status**: Active Development - Test Coverage & Workspace Implementation  
**Updated**: 2025-11-19

---

## Current Focus

1. **Improve Test Coverage** - Target 80%+ for server and client
2. **Implement Workspaces** - Multi-tenant document/chat organization
3. **RabbitMQ & Redis Integration** - Event-driven architecture with caching
4. **Shared Library** - Consolidate common code between server and workers

---

## Architecture Overview

### Client (React + TypeScript)
- **Location**: `packages/client/`
- **Structure**: Component-based with Redux state management
- **Testing**: Vitest + Testing Library (17 test files, need expansion)
- **Features**: Auth, Chat, Documents, Workspace UI (in progress)

### Server (Flask + Python)
- **Location**: `packages/server/`
- **Structure**: Domain-driven design with clean architecture
- **Testing**: Pytest (36 test files, need higher coverage)
- **Features**: REST API, WebSocket chat, Auth, Document management

### Shared Library (Python)
- **Location**: `packages/shared/python/`
- **Purpose**: Common types, models, interfaces, and utilities
- **Contents**: SQLAlchemy models, RAG interfaces, messaging, caching
- **Dependencies**: Redis (optional), RabbitMQ, PostgreSQL, Qdrant

### Workers (7 services - Future)
- **Location**: `packages/workers/`
- **Status**: Structured but not priority for current phase
- **Services**: ingestion, embeddings, graph, enrichment, query, retriever, notify

## Infrastructure Services

```
PostgreSQL (5432)  - Main database
RabbitMQ (5672)    - Message queue (ready, not actively used)
Redis (6379)       - Cache (optional, graceful degradation)
Qdrant (6333)      - Vector database
MinIO (9000)       - Object storage
Ollama (11434)     - Local LLM
```

## Docker Compose Organization

- `docker-compose.yml` - Core infrastructure (6 services above)
- `docker-compose.dev.yml` - Dev server + client with hot-reload
- `docker-compose.prod.yml` - Production builds
- `docker-compose.elk.yml` - Optional ELK monitoring stack

---

## High Priority Tasks

### 1. Test Coverage (In Progress)
- **Server**: Currently ~40%, target 80%+
  - Add unit tests for all services (workspace, chat, document, user)
  - Add integration tests for API endpoints
  - Add tests for RabbitMQ publishing and Redis caching
- **Client**: Currently ~50%, target 80%+
  - Add unit tests for Redux slices and hooks
  - Add component tests for workspace features
  - Add integration tests for API interactions

### 2. Workspace Implementation
- **Database**: Create Alembic migration for workspace schema
  - `workspaces` table (id, name, description, user_id, created_at)
  - `rag_configs` table (workspace_id, embedding_model, retriever_type, chunk_size, etc.)
  - Update `documents` and `chat_sessions` with workspace_id foreign key
- **Server**: Implement WorkspaceService with Redis caching
  - CRUD operations for workspaces
  - RAG config management per workspace
  - Publish workspace events to RabbitMQ
- **Client**: Build workspace UI components
  - WorkspaceSelector dropdown
  - WorkspaceSettings modal
  - Update document/chat UIs to be workspace-aware

### 3. Move Code to Shared Library
- Move common RAG components from server to shared
- Move common utilities and helpers to shared
- Ensure all imports work correctly

### 4. Redis Integration (Optional)
- Cache workspace data with TTL
- Cache RAG configs
- Cache user sessions
- Gracefully degrade when Redis unavailable

---

## Project Architecture

### Tech Stack

**Backend**:
- Flask 3.x with Flask-SocketIO for WebSockets
- SQLAlchemy 2.x ORM with Alembic migrations
- PostgreSQL 16 for relational data
- Qdrant for vector embeddings
- MinIO for object storage
- Optional: Redis for caching, RabbitMQ for async processing

**Frontend**:
- React 19 + TypeScript
- Redux Toolkit for state management
- TailwindCSS for styling
- Vite for dev server and builds
- Socket.IO client for real-time chat

**Testing**:
- Server: pytest + pytest-cov + testcontainers
- Client: vitest + @testing-library/react
- Target: 80%+ coverage for both

### Event Flow

```
1. User uploads document
   └──> Server receives file
        └──> DocumentService.process_document_upload()
             ├──> Upload to MinIO
             ├──> Save to PostgreSQL
             └──> Publish "document.uploaded" to RabbitMQ ✅

2. Ingestion Worker consumes "document.uploaded"
   ├──> Parse document (PDF, TXT) (TODO)
   ├──> Chunk text (TODO)
   ├──> Store chunks in PostgreSQL (TODO)
   └──> Publish "document.chunks.ready" (TODO)

3. Embeddings Worker consumes "embeddings.generate"
   ├──> Fetch chunks from PostgreSQL (TODO)
   ├──> Generate embeddings with Ollama (TODO)
   ├──> Upsert vectors to Qdrant (TODO)
   └──> Publish "vector.index.updated" (TODO)

4. Graph Worker consumes "document.graph.build"
   ├──> Extract entities (TODO)
   ├──> Extract relationships (TODO)
   ├──> Build graph (TODO)
   └──> Publish "graph.build.complete" (TODO)
```

---

## What's Implemented

### Fully Implemented ✅

1. **Server Infrastructure**
   - Flask API with domain-driven design
   - PostgreSQL database with SQLAlchemy
   - MinIO blob storage
   - RabbitMQ publisher (fully working)
   - Socket.IO WebSocket for real-time chat
   - JWT authentication
   - Rate limiting and security middleware

2. **Client Application**
   - React 19 with TypeScript
   - Feature-based architecture
   - Redux Toolkit for state management
   - Socket.IO client for real-time updates
   - Authentication flows (login, signup)
   - Chat interface with streaming
   - Document upload interface

3. **Shared Library**
   - 8 core data types
   - 14 abstract interfaces (9 vector RAG, 5 graph RAG)
   - 8 event schemas
   - 2 orchestrators (VectorRAG, GraphRAG structure)

4. **Infrastructure**
   - All 6 infrastructure services configured
   - Docker Compose with profiles
   - Multi-stage Dockerfiles
   - Task runner with clean commands
   - ELK monitoring stack

### Partially Implemented (TODOs) ⏳

1. **Workers** - Structure complete, logic needs implementation
   - ✅ RabbitMQ connection and message handling
   - ✅ Event parsing and acknowledgment
   - ✅ Graceful shutdown
   - ⏳ Core processing logic (marked with TODOs)
   
2. **Server RabbitMQ Integration**
   - ✅ Publisher implemented and working
   - ✅ Document upload publishes events
   - ⏳ Other domains (chat, users) not publishing yet

---

## Next Steps for Development

## Quick Start

### Local Development (Recommended)

```bash
# 1. Start infrastructure services
task up-infra

# 2. Run server (terminal 1)
cd packages/server && poetry install && poetry run python src/api.py

# 3. Run client (terminal 2)
cd packages/client && bun install && bun run dev

# Access:
#   - Client: http://localhost:3000
#   - Server API: http://localhost:5000
#   - MinIO Console: http://localhost:9001
#   - Qdrant UI: http://localhost:6334
#   - RabbitMQ Management: http://localhost:15672
```

### Docker Development

```bash
# Start everything in development mode
task up-dev

# View logs
task logs-server-dev
task logs-client-dev

# Stop all services
task down
```

### Running Tests

```bash
# Server tests
cd packages/server
task test              # All tests with coverage
task test:unit         # Fast unit tests only
task test:integration  # Integration tests (requires Docker)

# Client tests
cd packages/client
task test              # All tests
task test:coverage     # With coverage report
task test:watch        # Watch mode
```

---

## Common Development Tasks

```bash
# Format and lint code
task server:format     # Format server code
task client:format     # Format client code
task check             # Run all checks (both)

# Build Docker images
task build-dev         # Build dev images
task build             # Build production images

# View logs
task logs-server-dev   # Server logs
task logs-postgres     # Database logs
task logs-redis        # Cache logs

# Clean up
task down              # Stop all services
task clean             # Remove containers and volumes
```

---

## Development Tips

1. **Use local development** for faster iteration (hot-reload, easier debugging)
2. **Redis and RabbitMQ** are optional - server degrades gracefully if unavailable
3. **Run unit tests** frequently - they're fast and catch most issues
4. **Integration tests** require Docker - use testcontainers for isolated DB tests
5. **Check logs** with `task logs-*` commands when debugging issues

---

## Documentation

- `README.md` - Project overview and features
- `docs/architecture.md` - System architecture and design patterns
- `docs/testing.md` - Testing strategy and guidelines
- `docs/docker.md` - Docker setup and configuration
- `docs/contributing.md` - Contribution guidelines
- `packages/server/README.md` - Server API documentation
- `packages/client/README.md` - Client app documentation

---

**Last Updated**: 2025-11-19
