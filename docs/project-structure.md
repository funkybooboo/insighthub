# Project Structure

Clean, intuitive file organization for InsightHub monorepo with dual RAG system architecture.

## Repository Overview

```
insighthub/
- packages/               # Monorepo packages
|   - shared/            # Shared libraries and types
|   - server/            # Python Flask backend
|   - client/            # React frontend
|   - cli/               # Command-line interface
|   - workers/           # Background processing workers
- docs/                  # Documentation
|   - planning/          # Project planning documents
|   - project-management/# Project management docs
|   - rag/              # RAG system documentation
- elk/                   # ELK monitoring configuration
- .github/workflows/      # CI/CD workflows
- docker-compose*.yml     # Service orchestration files
- Taskfile.yml           # Root task runner
- README.md
```

## Package Structure

### 1. Shared Library (`packages/shared/`)

Common types, interfaces, and utilities used across server and workers.

#### Python Shared (`packages/shared/python/`)
```
packages/shared/python/
- src/
|   - shared/
|   |   - types/             # Core data types
|   |   |   - common.py      # PrimitiveValue, MetadataValue
|   |   |   - document.py    # Document, Chunk
|   |   |   - graph.py       # GraphNode, GraphEdge
|   |   |   - rag.py         # RagConfig, ChunkerConfig
|   |   |   - retrieval.py   # RetrievalResult, SearchResult
|   |   - interfaces/        # Abstract interfaces
|   |   |   - vector/        # Vector RAG interfaces
|   |   |   |   - parser.py
|   |   |   |   - chunker.py
|   |   |   |   - embedder.py
|   |   |   |   - store.py
|   |   |   |   - retriever.py
|   |   |   |   - ranker.py
|   |   |   |   - context.py
|   |   |   |   - llm.py
|   |   |   |   - formatter.py
|   |   |   - graph/         # Graph RAG interfaces
|   |   |       - entity.py
|   |   |       - relation.py
|   |   |       - builder.py
|   |   |       - store.py
|   |   |       - retriever.py
|   |   - events/            # RabbitMQ event schemas
|   |   |   - document.py
|   |   |   - embedding.py
|   |   |   - graph.py
|   |   |   - query.py
|   |   - orchestrators/     # High-level RAG pipelines
|   |   |   - vector_rag.py  # VectorRAGIndexer, VectorRAG
|   |   |   - graph_rag.py   # GraphRAGIndexer, GraphRAG
|   |   - rabbitmq/          # RabbitMQ utilities
|   |   - exceptions/        # Custom exceptions
|   |   - logging/           # Structured logging
|   |   - models/            # Shared data models
|   |   - storage/           # Storage utilities
- tests/                    # Tests for shared components
- pyproject.toml
- poetry.lock
- README.md
```

#### TypeScript Shared (`packages/shared/typescript/`)
```
packages/shared/typescript/
- src/
|   - types/               # Shared TypeScript types
|   |   - api.ts         # API request/response types
|   |   - chat.ts        # Chat-related types
|   |   - document.ts    # Document types
|   |   - workspace.ts   # Workspace types
|   |   - user.ts        # User types
|   - utils/               # Shared utilities
- package.json
- README.md
```

**Usage:**
```python
# Python
from shared.types import Document, Chunk
from shared.events import DocumentUploadedEvent
from shared.interfaces.vector import EmbeddingEncoder
from shared.orchestrators.vector_rag import VectorRAG

# TypeScript
import { ApiDocument, ChatMessage } from '@insighthub/shared/types';
```

### 2. Server (`packages/server/`)

Flask backend with clean architecture (domains + infrastructure).

```
packages/server/
- src/
|   - domains/           # Business logic by domain
|   |   - auth/         # Authentication domain
|   |   |   - routes.py       # Auth API routes
|   |   |   - service.py      # Auth business logic
|   |   |   - dtos.py         # Data transfer objects
|   |   |   - exceptions.py   # Domain exceptions
|   |   - chat/         # Chat domain
|   |   |   - routes.py       # Chat API routes
|   |   |   - service.py      # Chat business logic
|   |   |   - socket_handlers.py # WebSocket handlers
|   |   |   - dtos.py         # Data transfer objects
|   |   |   - mappers.py      # Data mapping
|   |   |   - exceptions.py   # Domain exceptions
|   |   - documents/    # Document management
|   |   |   - routes.py       # Document API routes
|   |   |   - service.py      # Document business logic
|   |   |   - dtos.py         # Data transfer objects
|   |   |   - mappers.py      # Data mapping
|   |   |   - exceptions.py   # Domain exceptions
|   |   - workspaces/    # Workspace management
|   |   |   - routes.py       # Workspace API routes
|   |   |   - service.py      # Workspace business logic
|   |   |   - dtos.py         # Data transfer objects
|   |   |   - mappers.py      # Data mapping
|   |   |   - exceptions.py   # Domain exceptions
|   |   - users/         # User management
|   |   |   - service.py      # User business logic
|   |   |   - mappers.py      # Data mapping
|   |   |   - exceptions.py   # Domain exceptions
|   |   - health/        # Health checks
|   |   |   - routes.py       # Health check endpoints
|   |   - status/        # Status updates
|   |       - socket_handlers.py # Status WebSocket handlers
|   - infrastructure/    # External integrations
|   |   - auth/          # Authentication infrastructure
|   |   |   - jwt_utils.py    # JWT utilities
|   |   |   - middleware.py   # Auth middleware
|   |   - database/      # Database infrastructure
|   |   - middleware/    # HTTP middleware
|   |   |   - security.py     # Security headers
|   |   |   - logging.py      # Request logging
|   |   |   - rate_limiting.py # Rate limiting
|   |   |   - validation.py   # Request validation
|   |   |   - monitoring.py   # Metrics and monitoring
|   |   - socket/        # WebSocket infrastructure
|   |   - rag/           # RAG system implementations
|   |       - rag.py          # RAG interface
|   |       - vector_rag.py    # Vector RAG implementation
|   |       - factory.py      # RAG factory
|   |       - chunking/       # Text chunking strategies
|   |       - embeddings/      # Embedding models
|   |       - vector_stores/  # Vector store implementations
|   - api.py             # Main Flask application
|   - config.py          # Application configuration
|   - context.py         # Application context
- tests/                # Test suite
|   - unit/             # Unit tests with dummy implementations
|   - integration/      # Integration tests with testcontainers
|   - conftest.py       # Test configuration
- migrations/           # Database migrations
- docs/                 # API documentation
- bruno/                # API testing (Bruno)
- pyproject.toml        # Poetry configuration
- poetry.lock           # Dependency lock file
- Taskfile.yml          # Task automation
- Dockerfile           # Docker configuration
- openapi.yaml         # OpenAPI specification
- README.md            # This file
```

**Domain Structure Pattern:**
Each domain follows clean architecture principles:
- **routes.py**: API endpoints and request handling
- **service.py**: Business logic and use cases
- **dtos.py**: Data transfer objects for API communication
- **mappers.py**: Data mapping between layers
- **exceptions.py**: Domain-specific exceptions

### 3. Client (`packages/client/`)

React frontend with feature-based organization.

```
packages/client/
- src/
|   - components/              # React components
|   |   - auth/              # Authentication components
|   |   |   - LoginForm.tsx
|   |   |   - SignupForm.tsx
|   |   |   - UserMenu.tsx
|   |   - chat/              # Chat interface components
|   |   |   - ChatBot.tsx
|   |   |   - ChatInput.tsx
|   |   |   - ChatMessages.tsx
|   |   |   - ChatSidebar.tsx
|   |   - settings/          # Settings components
|   |   |   - ProfileSettings.tsx
|   |   |   - RagConfigSettings.tsx
|   |   |   - ThemePreferences.tsx
|   |   - upload/            # Document upload components
|   |   |   - FileUpload.tsx
|   |   |   - DocumentList.tsx
|   |   |   - DocumentManager.tsx
|   |   - workspace/         # Workspace management
|   |   |   - WorkspaceSelector.tsx
|   |   |   - WorkspaceSettings.tsx
|   |   - ui/                # Reusable UI components
|   - pages/                 # Page-level components
|   |   - WorkspacesPage.tsx
|   |   - WorkspaceDetailPage.tsx
|   |   - SettingsPage.tsx
|   - services/              # API and external services
|   |   - api.ts             # REST API client
|   |   - socket.ts          # WebSocket/Socket.IO client
|   - store/                 # Redux state management
|   |   - slices/            # Redux slices
|   |   |   - authSlice.ts
|   |   |   - chatSlice.ts
|   |   |   - workspaceSlice.ts
|   |   |   - themeSlice.ts
|   |   - index.ts           # Store configuration
|   - types/                 # TypeScript type definitions
|   |   - chat.ts            # Chat-related types
|   |   - workspace.ts       # Workspace-related types
|   |   - api.ts             # API response types
|   - lib/                   # Utilities and helpers
|   |   - utils.ts           # General utilities
|   |   - chatStorage.ts     # Local storage helpers
|   |   - validation.ts      # Input validation
|   - hooks/                 # Custom React hooks
|   |   - useStatusUpdates.ts # WebSocket status hook
|   - test/                  # Test setup and utilities
|   - App.tsx                # Main application component
|   - main.tsx               # Application entry point
|   - vite-env.d.ts          # Vite type definitions
- public/                    # Static assets
- .storybook/                # Storybook configuration
- docs/                      # Component documentation
- package.json               # Dependencies and scripts
- bun.lock                  # Dependency lock file
- Taskfile.yml              # Task automation
- vite.config.ts            # Vite configuration
- vitest.config.ts          # Vitest configuration
- README.md                 # This file
```

**Feature Module Pattern:**
- Each feature is self-contained with components, hooks, store, services, types
- Features export clean public API
- Shared code goes in `src/lib/` and `src/components/ui/`

### 4. CLI (`packages/cli/`)

Command-line interface for terminal access to InsightHub features.

```
packages/cli/
- src/
|   - commands/              # Command implementations
|   |   - auth.ts          # Authentication commands
|   |   - chat.ts          # Chat commands
|   |   - docs.ts          # Document commands
|   |   - workspaces.ts    # Workspace commands
|   |   - system.ts        # System commands
|   - lib/                 # Utilities and helpers
|   |   - api.ts           # API client
|   |   - config.ts        # Configuration management
|   |   - utils.ts         # General utilities
|   |   - ui.ts            # Terminal UI helpers
|   - types/               # TypeScript type definitions
|   - cli.ts               # Main CLI entry point
- tests/                   # Test files
- package.json             # Dependencies and scripts
- bun.lock               # Dependency lock file
- tsconfig.json          # TypeScript configuration
- README.md              # This file
```

### 5. Workers (`packages/workers/`)

Background processing workers for document processing and RAG operations.

```
packages/workers/
- parser/                 # Document parsing worker
|   - src/
|   |   - main.py        # Worker entry point
|   |   - handlers.py    # Event handlers
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- chunker/                # Text chunking worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- embedder/               # Embedding generation worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- indexer/                # Vector indexing worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- retriever/              # Document retrieval worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- chucker/                # Document chunking worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- connector/              # External connector worker
|   - src/
|   |   - main.py
|   |   - handlers.py
|   - Dockerfile
|   - pyproject.toml
|   - README.md
- enricher/              # Content enrichment worker
    - src/
    |   - main.py
    |   - handlers.py
    - Dockerfile
    - pyproject.toml
    - README.md
```

**Worker Structure Pattern:**
All workers follow consistent structure:
- `src/main.py`: Worker entry point with RabbitMQ setup
- `src/handlers.py`: Event handlers for processing
- `Dockerfile`: Multi-stage build (development + production)
- `pyproject.toml`: Dependencies and configuration
- `README.md`: Worker-specific documentation

## Docker Compose Files

Multiple compose files for different deployment scenarios:

### 1. `docker-compose.yml` - Infrastructure Services
Core infrastructure services required for all deployments:
- PostgreSQL (port 5432) - Primary database
- MinIO (ports 9000, 9001) - Object storage
- Ollama (port 11434) - LLM service
- RabbitMQ (ports 5672, 15672) - Message queue
- Qdrant (ports 6333, 6334) - Vector database

### 2. `docker-compose.dev.yml` - Development Services
Development server and client with hot reload:
- server-dev (port 5000) - Flask with auto-reload
- client-dev (port 3000) - Vite dev server

### 3. `docker-compose.prod.yml` - Production Services
Production-optimized server and client:
- server-prod (port 8000) - Flask production
- client-prod (port 80) - Nginx static server

### 4. `docker-compose.workers.yml` - Background Workers
All processing workers (uses `--profile workers`):
- parser, chunker, embedder, indexer
- retriever, chucker, connector, enricher

### 5. `docker-compose.elk.yml` - ELK Monitoring Stack
Comprehensive monitoring and logging:
- Elasticsearch (port 9200) - Log storage and search
- Logstash (port 5044) - Log processing
- Kibana (port 5601) - Monitoring dashboard
- Filebeat - Log collection from containers

## Task Files

### Root `Taskfile.yml`

Main orchestration commands for the entire project:

```bash
# Infrastructure Management
task up-infra          # Start infrastructure only
task up-dev            # Start infrastructure + dev server/client
task up                # Start infrastructure + production server/client
task up-workers        # Start all workers
task up-full           # Start everything (infra + dev + workers)
task up-elk            # Start ELK monitoring
task down              # Stop all services

# Development
task build-dev         # Build development images
task build             # Build production images
task restart-dev       # Restart development services

# Monitoring
task logs              # View all logs
task logs-server-dev   # View server logs
task logs-client-dev   # View client logs
task logs-workers      # View all worker logs

# Quality Assurance
task check             # Run all checks (server + client)
task format            # Format all code
task lint              # Lint all code
task test              # Run all tests
```

### Package `Taskfile.yml`

Each package has its own Taskfile with consistent commands:

```bash
# Server tasks (packages/server/)
task server            # Start development server
task format            # Format code (Black + isort)
task lint              # Run linter (Ruff)
task typecheck         # Type checking (MyPy)
task test              # Run tests (Pytest)
task check             # Run all quality checks

# Client tasks (packages/client/)
task dev               # Start Vite dev server
task build             # Build for production
task format            # Format code (Prettier)
task lint              # Run linter (ESLint)
task test              # Run tests (Vitest)
task check             # Run all quality checks

# Worker tasks (packages/workers/{worker}/)
task start             # Start worker
task build             # Build worker image
task test              # Run worker tests
```

## Documentation Structure

```
docs/
- planning/                  # Project planning documents
|   - idea.md              # Original project proposal
|   - requirements.md       # System requirements
|   - high-level-design.md  # High-level architecture
|   - low-level-design.md  # Detailed design
- project-management/        # Project management
|   - todo.md              # Project TODOs
- rag/                      # RAG system documentation
|   - comparison.md         # Vector vs Graph RAG comparison
|   - vector-rag-architecture.md # Vector RAG details
|   - graph-rag-architecture.md  # Graph RAG details
- architecture.md           # System architecture overview
- client-user-flows.md     # Detailed user interaction flows
- project-structure.md     # This file
- testing.md               # Testing strategy and guide
- docker.md                # Docker setup and usage
- contributing.md          # Development guidelines
- streaming.md             # WebSocket implementation
- taskfile-setup.md        # Task configuration
- github-actions.md        # CI/CD workflows
- changelog.md            # Project changelog
```

## Key Design Principles

### 1. Clean Architecture
- **Separation of Concerns**: Clear boundaries between domains, infrastructure, and presentation
- **Dependency Injection**: Components receive dependencies via constructors
- **Interface-Driven**: Abstract interfaces define contracts between layers
- **Domain-First**: Business logic drives infrastructure decisions

### 2. Feature-Based Organization
- **Client**: Features colocate related code (components, hooks, store, services)
- **Server**: Domains group business logic with infrastructure support
- **Workers**: Each worker is an independent microservice

### 3. Type Safety
- **Python**: Strict mypy configuration, no `Any` types allowed
- **TypeScript**: Strict mode enabled, explicit types required
- **Shared Types**: Single source of truth for data structures

### 4. Consistent Structure
- All workers have identical file structure
- All Dockerfiles follow multi-stage build pattern
- All packages have Taskfile with consistent commands
- All domains follow same architectural pattern

### 5. ASCII-Only Policy
- No emojis in code, comments, commit messages, or documentation
- Standard ASCII punctuation throughout
- Better compatibility and searchability

### 6. Testing Philosophy
- **Unit Tests**: Use dummy implementations, not mocks
- **Integration Tests**: Use testcontainers for real services
- **E2E Tests**: Use Playwright for user flows
- **API Tests**: Use Bruno for REST API testing

## Development Workflow

### Quick Start (Local Development)

```bash
# 1. Start infrastructure services
task up-infra

# 2. Start server locally (terminal 1)
cd packages/server
poetry install
task server

# 3. Start client locally (terminal 2)
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

# View logs for specific services
task logs-server-dev
task logs-client-dev
task logs-workers
```

### Production Deployment

```bash
# Build production images
task build

# Deploy production services
task up

# Enable monitoring
task up-elk
```

## Port Reference

| Service          | Port(s) | Description                    |
|------------------|----------|--------------------------------|
| Client Dev       | 3000     | Vite development server        |
| Client Prod      | 80       | Nginx static server           |
| Server Dev       | 5000     | Flask with auto-reload         |
| Server Prod      | 8000     | Flask production              |
| PostgreSQL      | 5432     | Primary database              |
| MinIO API       | 9000     | Object storage API           |
| MinIO Console   | 9001     | Web UI for MinIO            |
| Ollama          | 11434    | LLM service                  |
| RabbitMQ        | 5672     | AMQP message protocol         |
| RabbitMQ Mgmt   | 15672    | Management UI                |
| Qdrant API       | 6333     | Vector database API          |
| Qdrant UI        | 6334     | Web UI for Qdrant           |
| Elasticsearch   | 9200     | Search engine                |
| Kibana          | 5601     | Monitoring dashboard         |

## Next Steps

For detailed information about specific components, see:

- [Server README](../packages/server/README.md) - Flask backend details
- [Client README](../packages/client/README.md) - React frontend details
- [CLI README](../packages/cli/README.md) - Command-line interface
- [Shared Library](../packages/shared/) - Common types and utilities
- [Architecture Overview](architecture.md) - System architecture
- [Client User Flows](client-user-flows.md) - Detailed user interactions
- [Testing Guide](testing.md) - Comprehensive testing documentation