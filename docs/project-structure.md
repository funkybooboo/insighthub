# Project Structure

Clean, intuitive file organization for the InsightHub monorepo.

## Repository Overview

```
insighthub/
├── packages/               # Monorepo packages
│   ├── shared/            # Shared libraries
│   ├── server/            # Python Flask backend
│   ├── client/            # React frontend
│   ├── workers/           # Background workers (7 workers)
│   └── cli/               # Command-line interface
├── docs/                  # Documentation
├── elk/                   # ELK monitoring configuration
├── docker-compose*.yml    # Service orchestration (5 files)
├── Taskfile.yml           # Root task runner
└── README.md
```

## Package Structure

### 1. Shared Library (`packages/shared/python/`)

Common types, interfaces, and utilities used across server and workers.

```
packages/shared/python/
├── src/shared/
│   ├── types/             # Core data types
│   │   ├── common.py      # PrimitiveValue, MetadataValue
│   │   ├── document.py    # Document, Chunk
│   │   ├── graph.py       # GraphNode, GraphEdge
│   │   ├── rag.py         # RagConfig, ChunkerConfig
│   │   └── retrieval.py   # RetrievalResult, SearchResult
│   ├── interfaces/        # Abstract interfaces
│   │   ├── vector/        # Vector RAG interfaces (9 interfaces)
│   │   │   ├── parser.py
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py
│   │   │   ├── store.py
│   │   │   ├── retriever.py
│   │   │   ├── ranker.py
│   │   │   ├── context.py
│   │   │   ├── llm.py
│   │   │   └── formatter.py
│   │   └── graph/         # Graph RAG interfaces (5 interfaces)
│   │       ├── entity.py
│   │       ├── relation.py
│   │       ├── builder.py
│   │       ├── store.py
│   │       └── retriever.py
│   ├── events/            # RabbitMQ event schemas (8 events)
│   │   ├── document.py
│   │   ├── embedding.py
│   │   ├── graph.py
│   │   └── query.py
│   ├── orchestrators/     # High-level RAG pipelines
│   │   ├── vector_rag.py  # VectorRAGIndexer, VectorRAG
│   │   └── graph_rag.py   # GraphRAGIndexer, GraphRAG
│   ├── rabbitmq/          # RabbitMQ utilities
│   ├── exceptions/        # Custom exceptions
│   ├── logging/           # Structured logging
│   ├── models/            # Shared data models (dataclasses)
│   ├── rag/               # Concrete RAG implementations
│   └── storage/           # Storage utilities
├── pyproject.toml
├── poetry.lock
└── README.md
```

**Usage:**
```python
from shared.types import Document, Chunk
from shared.events import DocumentUploadedEvent
from shared.interfaces.vector import EmbeddingEncoder
from shared.orchestrators.vector_rag import VectorRAG
```

### 2. Server (`packages/server/`)

Flask backend with clean architecture (domains + infrastructure).

```
packages/server/
├── src/
│   ├── domains/           # Business logic (feature-based)
│   │   ├── auth/          # Authentication
│   │   ├── chat/          # Chat sessions
│   │   ├── documents/     # Document management
│   │   ├── health/        # Health checks
│   │   └── users/         # User management
│   ├── infrastructure/    # External integrations
│   │   ├── auth/          # JWT, middleware
│   │   ├── database/      # PostgreSQL
│   │   ├── llm/           # LLM providers (Ollama, OpenAI, Claude, HuggingFace)
│   │   ├── rag/           # RAG implementations
│   │   │   ├── chunking/
│   │   │   ├── embeddings/
│   │   │   ├── vector_stores/
│   │   │   └── graph_stores/
│   │   ├── storage/       # Blob storage (MinIO, S3, FileSystem)
│   │   ├── messaging/     # RabbitMQ publisher
│   │   ├── middleware/    # Logging, rate limiting, security
│   │   ├── socket/        # Socket.IO handlers
│   │   ├── errors/        # Error handling
│   │   └── factories/     # Dependency injection
│   ├── api.py             # Flask application entry
│   ├── config.py          # Configuration
│   └── context.py         # Application context
├── tests/
│   ├── unit/              # Unit tests (with dummies)
│   └── integration/       # Integration tests (with testcontainers)
├── Dockerfile
├── docker-entrypoint.sh
├── pyproject.toml
├── poetry.lock
└── Taskfile.yml
```

**Domain Structure** (example: `domains/chat/`):
```
domains/chat/
├── models.py              # Data models
├── repositories.py        # Data access layer
├── service.py             # Business logic
├── routes.py              # REST API endpoints
├── socket_handlers.py     # WebSocket handlers
├── dtos.py                # Data transfer objects
├── mappers.py             # Model <-> DTO mapping
├── exceptions.py          # Domain-specific exceptions
└── __init__.py
```

### 3. Client (`packages/client/`)

React frontend with feature-based organization.

```
packages/client/
├── src/
│   ├── features/          # Feature modules (colocation)
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── SignupForm.tsx
│   │   │   │   ├── UserMenu.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── store/
│   │   │   │   └── authSlice.ts
│   │   │   └── index.ts   # Public API
│   │   ├── chat/
│   │   │   ├── components/
│   │   │   │   ├── ChatBot.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── ChatMessages.tsx
│   │   │   │   └── ChatSidebar.tsx
│   │   │   ├── services/
│   │   │   │   └── socket.ts
│   │   │   ├── store/
│   │   │   │   └── chatSlice.ts
│   │   │   ├── types/
│   │   │   │   └── chat.ts
│   │   │   └── index.ts
│   │   └── documents/
│   │       ├── components/
│   │       │   ├── DocumentManager.tsx
│   │       │   ├── DocumentList.tsx
│   │       │   └── FileUpload.tsx
│   │       └── index.ts
│   ├── shared/            # Shared utilities
│   │   ├── components/    # UI components (buttons, etc.)
│   │   ├── lib/           # Utility functions
│   │   ├── services/      # API client
│   │   ├── assets/        # Images, sounds
│   │   └── themeSlice.ts
│   ├── store/             # Redux store configuration
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── Dockerfile
├── docker-entrypoint.sh
├── package.json
├── bun.lock
├── vite.config.ts
├── vitest.config.ts
└── Taskfile.yml
```

**Feature Module Pattern:**
- Each feature is self-contained with its components, hooks, store, services, types
- Features export a clean public API via `index.ts`
- Shared code goes in `src/shared/`

### 4. Workers (`packages/workers/`)

Seven background workers with consistent structure.

```
packages/workers/
├── ingestion/             # Document parsing and chunking
├── embeddings/            # Vector generation and Qdrant indexing
├── graph/                 # Entity extraction and graph construction
├── enrichment/            # External knowledge fetching
├── query/                 # Pre-compute query context
└── retriever/             # Live internet data fetching
```

**Worker Structure** (all workers follow this pattern):
```
packages/workers/{worker}/
├── src/
│   ├── main.py            # Worker entry point with RabbitMQ setup
│   ├── handlers/          # Event handlers (TODO)
│   ├── utils/             # Worker-specific utilities (TODO)
│   └── __init__.py
├── Dockerfile             # Multi-stage build (development + production)
├── pyproject.toml
├── poetry.lock
├── README.md
└── Taskfile.yml
```

## Docker Compose Files

Five compose files for different concerns:

1. **`docker-compose.yml`** - Infrastructure services (always required)
   - PostgreSQL (port 5432)
   - MinIO (ports 9000, 9001)
   - Ollama (port 11434)
   - RabbitMQ (ports 5672, 15672)
   - Redis (port 6379)
   - Qdrant (ports 6333, 6334)

2. **`docker-compose.dev.yml`** - Development server + client
   - server-dev (port 5000, hot-reload)
   - client-dev (port 3000, Vite hot-reload)

3. **`docker-compose.prod.yml`** - Production server + client
   - server-prod (port 8000)
   - client-prod (port 80, nginx)

4. **`docker-compose.workers.yml`** - All 7 workers
   - Uses `--profile workers` flag
   - Each worker connects to infrastructure services

5. **`docker-compose.elk.yml`** - ELK monitoring stack
   - Elasticsearch (port 9200)
   - Logstash (port 5044)
   - Kibana (port 5601)
   - Filebeat (collects logs from all containers)

## Task Files

### Root `Taskfile.yml`

Main orchestration commands:

```bash
task up-infra          # Start infrastructure only
task up-dev            # Start infrastructure + dev server/client
task up                # Start infrastructure + production server/client
task up-workers        # Start all workers
task up-full           # Start everything (infra + dev + workers)
task up-elk            # Start ELK monitoring

task logs-server-dev   # View server logs
task logs-client-dev   # View client logs
task logs-workers      # View all worker logs

task build-dev         # Build development images
task build             # Build production images

task check             # Run all checks (server + client)
```

### Package `Taskfile.yml`

Each package (server, client, workers) has its own Taskfile:

```bash
# Server tasks
cd packages/server
task format            # Black + isort
task lint              # Ruff
task typecheck         # Mypy
task test              # Pytest
task check             # All checks

# Client tasks
cd packages/client
task format            # Prettier
task lint              # ESLint
task test              # Vitest
task check             # All checks
```

## Dockerfiles

All Dockerfiles follow multi-stage build pattern:

### Server Dockerfile

```dockerfile
FROM python:3.11-slim AS base           # Base dependencies
FROM base AS dependencies               # Production deps
FROM base AS dependencies-dev           # Dev deps
FROM dependencies-dev AS development    # Development target
FROM dependencies-dev AS builder        # Build and test
FROM dependencies AS production         # Production target
```

### Client Dockerfile

```dockerfile
FROM oven/bun:1.1.38-slim AS base       # Base dependencies
FROM base AS dependencies               # Install node_modules
FROM dependencies AS development        # Vite dev server
FROM dependencies AS builder            # Build static assets
FROM nginx:1.27-alpine AS production    # Serve with nginx
```

### Worker Dockerfiles

```dockerfile
FROM python:3.11-slim AS base           # Base dependencies
FROM base AS development                # Hot-reload development
FROM base AS production                 # Optimized production
```

## Key Design Principles

### 1. Feature-Based Organization

- **Client**: Features colocate related code (components, hooks, store, services)
- **Server**: Domains group business logic with infrastructure support
- **Workers**: Each worker is an independent microservice

### 2. Clean Architecture

- **Separation of concerns**: Domains, infrastructure, presentation
- **Dependency injection**: Factories create dependencies
- **Interface-driven**: Abstract interfaces in shared package

### 3. Type Safety

- **Python**: Strict mypy, no `Any` types
- **TypeScript**: Strict mode, explicit types
- **Shared types**: Single source of truth for data structures

### 4. Consistent Structure

- All workers have identical file structure
- All Dockerfiles follow multi-stage pattern
- All packages have Taskfile with same commands

### 5. ASCII Only

- No emojis in code, comments, or documentation
- Standard ASCII punctuation throughout
- Better compatibility and searchability

## Development Workflow

### Quick Start

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
task up-workers
```

### Containerized Development

```bash
# Start everything in containers
task build-dev
task up-full

# View logs
task logs-server-dev
task logs-client-dev
task logs-workers
```

### Production Deployment

```bash
# Build production images
task build

# Deploy
task up

# Enable monitoring
task up-elk
```

## Port Reference

| Service       | Port(s) | Description            |
|---------------|---------|------------------------|
| Client Dev    | 3000    | Vite dev server        |
| Client Prod   | 80      | Nginx static server    |
| Server Dev    | 5000    | Flask with auto-reload |
| Server Prod   | 8000    | Flask production       |
| PostgreSQL    | 5432    | Database               |
| MinIO API     | 9000    | Object storage         |
| MinIO Console | 9001    | Web UI                 |
| Ollama        | 11434   | LLM service            |
| RabbitMQ      | 5672    | AMQP protocol          |
| RabbitMQ Mgmt | 15672   | Management UI          |
| Redis         | 6379    | Cache                  |
| Qdrant API    | 6333    | Vector database        |
| Qdrant UI     | 6334    | Web UI                 |
| Elasticsearch | 9200    | Search engine          |
| Kibana        | 5601    | Monitoring UI          |

## Next Steps

See individual package READMEs for detailed documentation:

- [Server README](../packages/server/README.md)
- [Client README](../packages/client/README.md)
- [Shared Library README](../packages/shared/python/README.md)
- [Worker Documentation](../packages/workers/)
