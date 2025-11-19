# InsightHub - Clean Project Structure

## Overview

InsightHub is organized as a **clean, intuitive monorepo** with feature-based architecture and consistent patterns across all packages.

## Quick Reference

```bash
# Development
task up-infra          # Start databases and services only
task up-dev            # Start server + client (dev mode)
task up-workers-dev    # Start all 7 workers (dev mode)
task up-full           # Start everything (infra + dev + workers)

# Production
task up                # Start server + client (production)
task up-workers        # Start all 7 workers (production)

# Monitoring
task up-elk            # Start ELK stack (Elasticsearch, Logstash, Kibana)

# Logs
task logs-server-dev   # Development server logs
task logs-workers-dev  # Development worker logs
```

## File Organization

### 1. Docker Compose Files (4 files)

**`docker-compose.yml`** - Infrastructure (always required)
- PostgreSQL, MinIO, Ollama, RabbitMQ, Redis, Qdrant
- Base networks and volumes

**`docker-compose.dev.yml`** - Development stack
- server-dev (hot-reload)
- client-dev (Vite hot-reload)
- worker-*-dev (7 workers with hot-reload)
- Profiles: `dev`, `workers`

**`docker-compose.prod.yml`** - Production stack
- server-prod (optimized)
- client-prod (nginx)
- worker-*-prod (7 optimized workers)
- Profiles: `prod`, `workers`

**`docker-compose.elk.yml`** - Optional monitoring
- Elasticsearch, Logstash, Kibana, Filebeat

### 2. Shared Library (`packages/shared/python/`)

Centralized types, interfaces, and events for server + workers.

```
src/shared/
├── types/              # Core data structures
│   ├── common.py       # PrimitiveValue, MetadataValue
│   ├── document.py     # Document, Chunk
│   ├── graph.py        # GraphNode, GraphEdge
│   ├── rag.py          # RagConfig, ChunkerConfig
│   └── retrieval.py    # RetrievalResult, SearchResult
├── interfaces/         # Abstract interfaces
│   ├── vector/         # 9 Vector RAG interfaces
│   └── graph/          # 5 Graph RAG interfaces
├── events/             # RabbitMQ event schemas
│   ├── document.py     # DocumentUploadedEvent, etc.
│   ├── embedding.py    # EmbeddingGenerateEvent, etc.
│   ├── graph.py        # GraphBuildCompleteEvent
│   └── query.py        # QueryPrepareEvent, QueryReadyEvent
├── orchestrators/      # High-level RAG pipelines
│   ├── vector_rag.py   # VectorRAGIndexer, VectorRAG
│   └── graph_rag.py    # GraphRAGIndexer, GraphRAG (TODO)
├── rabbitmq/           # RabbitMQ utilities
├── exceptions/         # Custom exceptions (TODO)
├── logging/            # Structured logging (TODO)
└── storage/            # Storage utilities (TODO)
```

**Usage:**
```python
from shared.types import Document, Chunk
from shared.events import DocumentUploadedEvent
from shared.interfaces.vector import EmbeddingEncoder
from shared.orchestrators.vector_rag import VectorRAG
```

### 3. Server (`packages/server/`)

Flask backend with **domain-driven design**.

```
src/
├── domains/            # Feature modules
│   ├── auth/           # Authentication & authorization
│   ├── chat/           # Chat sessions & WebSocket
│   ├── documents/      # Document management
│   ├── health/         # Health checks
│   └── users/          # User management
├── infrastructure/     # External integrations
│   ├── auth/           # JWT, middleware
│   ├── database/       # PostgreSQL, SQLAlchemy
│   ├── llm/            # LLM providers (Ollama, OpenAI, Claude, HF)
│   ├── rag/            # RAG implementations
│   ├── storage/        # Blob storage (MinIO, S3, FileSystem)
│   ├── messaging/      # RabbitMQ publisher
│   ├── middleware/     # Logging, rate limiting, security
│   └── socket/         # Socket.IO handlers
├── api.py              # Flask app entry point
├── config.py           # Configuration
└── context.py          # Application context
```

**Domain Pattern** (example: `domains/chat/`):
```
chat/
├── models.py           # SQLAlchemy models
├── repositories.py     # Data access
├── service.py          # Business logic
├── routes.py           # REST API
├── socket_handlers.py  # WebSocket
├── dtos.py             # Data transfer objects
├── mappers.py          # Model <-> DTO conversion
└── exceptions.py       # Domain exceptions
```

### 4. Client (`packages/client/`)

React frontend with **feature-based colocation**.

```
src/
├── features/           # Self-contained feature modules
│   ├── auth/
│   │   ├── components/ # LoginForm, SignupForm, UserMenu, ProtectedRoute
│   │   ├── store/      # authSlice.ts
│   │   └── index.ts    # Public API
│   ├── chat/
│   │   ├── components/ # ChatBot, ChatInput, ChatMessages, ChatSidebar
│   │   ├── services/   # socket.ts
│   │   ├── store/      # chatSlice.ts
│   │   ├── types/      # chat.ts
│   │   └── index.ts    # Public API
│   └── documents/
│       ├── components/ # DocumentManager, DocumentList, FileUpload
│       └── index.ts    # Public API
├── shared/             # Cross-feature utilities
│   ├── components/     # UI components (Button, ThemeToggle)
│   ├── lib/            # Utilities, chatStorage
│   ├── services/       # API client
│   ├── assets/         # Images, sounds
│   └── themeSlice.ts   # Theme management
├── store/              # Redux store config
├── App.tsx
└── main.tsx
```

**Feature Pattern:**
- Colocate related code (components, hooks, store, services, types)
- Export clean public API via `index.ts`
- Keep shared code in `src/shared/`

### 5. Workers (`packages/workers/`)

Seven background workers with **identical structure**.

```
workers/
├── ingestion/          # Document parsing and chunking
├── embeddings/         # Vector generation and Qdrant indexing
├── graph/              # Entity extraction and graph construction
├── enrichment/         # External knowledge fetching
├── query/              # Pre-compute query context
├── retriever/          # Live internet data fetching
└── notify/             # System notifications
```

**Each worker:**
```
packages/workers/{worker}/
├── src/
│   ├── main.py         # RabbitMQ consumer entry point
│   ├── handlers/       # Event handlers (TODO)
│   ├── utils/          # Worker-specific utilities (TODO)
│   └── __init__.py
├── Dockerfile          # Multi-stage (development + production)
├── pyproject.toml      # Poetry dependencies
├── README.md
└── Taskfile.yml        # Worker-specific tasks
```

## Architecture Principles

### 1. Feature-Based Organization
- **Client**: Features colocate all related code
- **Server**: Domains group business logic
- **Workers**: Independent microservices

### 2. Clean Architecture
- Separation of concerns (domains, infrastructure, presentation)
- Dependency injection via factories
- Interface-driven design

### 3. Type Safety
- Python: Strict mypy, no `Any` types
- TypeScript: Strict mode, explicit types
- Shared types: Single source of truth

### 4. Consistency
- All workers have identical structure
- All Dockerfiles use multi-stage builds
- All packages have Taskfiles with same commands

### 5. ASCII Only
- No emojis anywhere
- Standard ASCII punctuation
- Better compatibility and searchability

## Development Workflows

### Quick Start (Local Development)

```bash
# 1. Start infrastructure
task up-infra

# 2. Run server locally (terminal 1)
cd packages/server
poetry install
task server

# 3. Run client locally (terminal 2)
cd packages/client
bun install
task dev

# 4. Optional: Start workers (terminal 3)
task up-workers-dev
```

### Containerized Development

```bash
# Start everything
task build-dev
task up-full

# View logs
task logs-server-dev
task logs-client-dev
task logs-workers-dev
```

### Production Deployment

```bash
# Build images
task build

# Deploy with workers
task up
task up-workers

# Enable monitoring
task up-elk
```

## Port Reference

| Service | Port | Description |
|---------|------|-------------|
| Client Dev | 3000 | Vite dev server |
| Client Prod | 3000 | Nginx static server |
| Server Dev | 5000 | Flask with auto-reload |
| Server Prod | 5000 | Flask production |
| PostgreSQL | 5432 | Database |
| MinIO API | 9000 | Object storage |
| MinIO Console | 9001 | Web UI |
| Ollama | 11434 | LLM service |
| RabbitMQ | 5672 | AMQP protocol |
| RabbitMQ Mgmt | 15672 | Management UI |
| Redis | 6379 | Cache |
| Qdrant API | 6333 | Vector database |
| Qdrant UI | 6334 | Web UI |
| Elasticsearch | 9200 | Search engine |
| Kibana | 5601 | Monitoring UI |

## Key Files

### Configuration
- `docker-compose.yml` - Infrastructure services
- `docker-compose.dev.yml` - Development server + client + workers
- `docker-compose.prod.yml` - Production server + client + workers
- `docker-compose.elk.yml` - Optional ELK monitoring
- `Taskfile.yml` - Root task runner
- `packages/*/Taskfile.yml` - Package-specific tasks

### Documentation
- `README.md` - Project overview
- `STRUCTURE.md` - This file (project structure)
- `docs/architecture.md` - System architecture
- `docs/project-structure.md` - Detailed structure guide
- `docs/PHASE2_STATUS.md` - Implementation status
- `docs/REFACTORING_COMPLETE.md` - Refactoring summary

### Docker
- `packages/server/Dockerfile` - Multi-stage server build
- `packages/client/Dockerfile` - Multi-stage client build
- `packages/workers/*/Dockerfile` - Multi-stage worker builds (all identical)

## Common Tasks

```bash
# Development
task up-infra              # Start infrastructure only
task up-dev                # Start dev server + client
task up-workers-dev        # Start dev workers
task up-full               # Start everything (dev)

# Production
task up                    # Start prod server + client
task up-workers            # Start prod workers

# Build
task build-dev             # Build all dev images
task build                 # Build all prod images
task build-server          # Build server only (prod)
task build-client          # Build client only (prod)

# Logs
task logs-server-dev       # Dev server logs
task logs-client-dev       # Dev client logs
task logs-workers-dev      # Dev worker logs
task logs-server           # Prod server logs
task logs-workers          # Prod worker logs

# Package tasks
task server:check          # Run all server checks (format, lint, typecheck, test)
task client:check          # Run all client checks (format, lint, test)
task check                 # Run checks for both server and client

# Cleanup
task down                  # Stop all services
task clean                 # Remove containers, images, volumes
```

## Next Steps

1. **For development**: See `README.md` for quick start
2. **For architecture**: See `docs/architecture.md`
3. **For testing**: See `docs/testing.md`
4. **For deployment**: See `docs/docker.md`
5. **For server details**: See `packages/server/README.md`
6. **For client details**: See `packages/client/README.md`
7. **For shared library**: See `packages/shared/python/README.md`

## Summary

InsightHub uses a clean, consistent structure:
- **4 docker-compose files** (infra, dev, prod, elk)
- **Feature-based organization** (client features, server domains, workers)
- **Shared library** (types, interfaces, events)
- **Multi-stage Dockerfiles** (development + production targets)
- **Task runners** (consistent commands across packages)
- **Type safety** (Python strict mypy, TypeScript strict mode)

Everything is organized for **clarity, consistency, and scalability**.
