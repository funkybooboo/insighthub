# InsightHub

A Python-based CLI application for intelligent document retrieval using advanced RAG (Retrieval-Augmented Generation) techniques with support for both vector and graph-based search.

## Architecture

InsightHub uses a **domain-driven design** architecture with clean separation of concerns:

- **CLI Interface**: Task-based command-line interface for all operations
- **Domain Layer**: Business logic organized by bounded contexts (workspace, document, chat)
- **Infrastructure Layer**: RAG workflows, LLM providers, vector/graph databases, storage
- **Data Layer**: PostgreSQL with pgvector, Qdrant, Neo4j, Redis cache

### Technology Stack

**Core:**
- Python 3.11+ with Poetry
- SQLAlchemy ORM + PostgreSQL (pgvector)
- Pydantic for configuration and validation
- Domain-driven design pattern

**RAG Components:**
- **Vector RAG**: Qdrant vector database, Sentence Transformers embeddings, reranking
- **Graph RAG**: Neo4j graph database, knowledge graph construction
- Dual retrieval strategies for enhanced accuracy

**LLM Providers:**
- Ollama (local, default) - llama3.2:1b + nomic-embed-text
- OpenAI GPT models
- Anthropic Claude models

**Infrastructure:**
- Redis for caching (optional, defaults to in-memory)
- MinIO (S3-compatible) for document storage
- Task runner for automation

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Poetry
- Task (https://taskfile.dev)

### Setup

```bash
# Start all infrastructure services
task up

# Install dependencies
task install

# Run migrations
task migrate-up

# Verify everything works
task health-check
```

The following services will be available:
- PostgreSQL: localhost:5432
- Qdrant UI: http://localhost:6334
- Neo4j Browser: http://localhost:7474
- MinIO Console: http://localhost:9001
- Ollama API: http://localhost:11434
- Redis: localhost:6379

### Basic Usage

```bash
# Create a workspace
task cli -- workspace create "My Project"

# List workspaces
task cli -- workspace list

# Select active workspace
task cli -- workspace select 1

# Add a document
task cli -- document add path/to/document.pdf

# List documents
task cli -- document list

# Start a chat session
task cli -- chat session create "Technical Questions"

# Send a message
task cli -- chat message send "What does this document say about X?"

# List chat history
task cli -- chat message list
```

## Project Structure

```
insighthub/
├── src/
│   ├── cli.py                          # CLI entry point
│   ├── config.py                       # Configuration management
│   ├── context.py                      # DI container
│   ├── domains/                        # Business domains
│   │   ├── default_rag_config/         # RAG configuration
│   │   └── workspace/                  # Main domain
│   │       ├── chat/                   # Chat sessions & messages
│   │       └── document/               # Document management
│   └── infrastructure/                 # Infrastructure layer
│       ├── models/                     # SQLAlchemy ORM models
│       ├── repositories/               # Data access layer
│       ├── rag/                        # RAG implementation
│       │   ├── steps/                  # RAG processing steps
│       │   │   ├── general/            # Parsing, chunking
│       │   │   ├── graph_rag/          # Graph RAG
│       │   │   └── vector_rag/         # Vector RAG, embedding, reranking
│       │   └── workflows/              # End-to-end workflows
│       ├── llm/                        # LLM provider abstractions
│       ├── vector_stores/              # Vector DB clients
│       ├── cache/                      # Caching implementations
│       ├── storage/                    # Blob storage (FS/S3)
│       └── sql_database.py             # Database connection
├── migrations/                         # SQL migration scripts
├── tests/                              # Test suite
│   ├── unit/                           # Unit tests
│   ├── integration/                    # Integration tests
│   └── e2e/                            # End-to-end tests
├── Taskfile.yml                        # Task automation
├── docker-compose.yml                  # Infrastructure services
└── pyproject.toml                      # Python dependencies
```

## Features

### Document Management
- Upload and parse documents (PDF, HTML, TXT)
- Automatic chunking with semantic/sliding window strategies
- Metadata enrichment for better retrieval
- Support for both filesystem and S3-compatible storage
- Document versioning and tracking per workspace

### RAG Capabilities

**Vector RAG:**
- Semantic search using Qdrant vector database
- Sentence Transformers embeddings
- Similarity-based retrieval with configurable top-k
- Result reranking for improved accuracy

**Graph RAG:**
- Knowledge graph construction in Neo4j
- Relationship-based retrieval
- Entity and concept extraction
- Graph traversal for context discovery

**Processing Pipeline:**
- Multi-format document parsing (PyPDF, BeautifulSoup)
- Intelligent text chunking with overlap
- Batch embedding for efficiency
- Configurable RAG parameters per workspace

### Chat Interface
- Multi-session support with history
- Streaming LLM responses
- Contextual retrieval from documents
- Session management and persistence

### Multi-Workspace Support
- Organize documents and chats by workspace
- Isolated configurations per workspace
- Easy workspace switching via CLI

### Caching & Performance
- Redis or in-memory caching
- Embedding cache to avoid recomputation
- Query result caching

## Development

### Common Tasks

```bash
# Code quality
task format          # Format code (Black + isort)
task lint            # Lint code (Ruff)
task type-check      # Type checking (mypy)
task check           # Run all quality checks

# Testing
task unit-test       # Run unit tests
task integration-test # Run integration tests
task e2e-test        # Run e2e tests
task test            # Run all tests

# Database
task migrate-up      # Apply migrations
task migrate-down    # Rollback migrations

# Infrastructure
task up              # Start Docker services
task down            # Stop services
task reset           # Full reset with migrations
task health-check    # Verify all services
```

### Running Tests

```bash
# Run all tests with coverage
task test

# Run specific test categories
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest tests/e2e

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/unit/test_chunking.py
```

### CLI Development

```bash
# Run CLI directly
poetry run python -m src.cli workspace list

# Or use task runner
task cli -- workspace list
task cli -- document add my-file.pdf
task cli -- chat message send "Hello!"
```

## Configuration

Environment variables and configuration options (see `src/config.py`):

**Database:**
- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://insighthub:insighthub@localhost:5432/insighthub`)

**Vector Store:**
- `QDRANT_HOST` - Qdrant host (default: `localhost`)
- `QDRANT_PORT` - Qdrant port (default: `6333`)

**Graph Database:**
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USERNAME` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password

**LLM Provider:**
- `LLM_PROVIDER` - Provider choice: `ollama`, `openai`, or `anthropic`
- `OLLAMA_BASE_URL` - Ollama API endpoint (default: `http://localhost:11434`)
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI)
- `ANTHROPIC_API_KEY` - Anthropic API key (if using Claude)
- `LLM_MODEL` - Model name for selected provider
- `EMBEDDING_MODEL` - Embedding model name

**Cache:**
- `CACHE_TYPE` - Cache backend: `memory` or `redis` (default: `memory`)
- `REDIS_URL` - Redis connection URL (if using Redis cache)

**Storage:**
- `STORAGE_TYPE` - Storage backend: `filesystem` or `s3` (default: `filesystem`)
- `STORAGE_PATH` - Filesystem storage path (default: `./storage`)
- `S3_ENDPOINT_URL` - S3-compatible endpoint (e.g., MinIO)
- `S3_BUCKET` - S3 bucket name
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key

**Logging:**
- `LOG_LEVEL` - Logging level (default: `INFO`)

## Docker Services

The `docker-compose.yml` defines 7 services:

| Service | Description | Ports |
|---------|-------------|-------|
| `postgres` | PostgreSQL 16 with pgvector extension | 5432 |
| `qdrant` | Vector database for semantic search | 6333, 6334 (UI) |
| `neo4j` | Graph database for knowledge graphs | 7474 (UI), 7687 |
| `ollama` | Local LLM service | 11434 |
| `ollama-setup` | Initializes Ollama models | - |
| `minio` | S3-compatible object storage | 9000, 9001 (console) |
| `redis` | Caching layer | 6379 |

## RAG Workflows

### Add Document Workflow
1. Parse document (extract text from PDF/HTML/TXT)
2. Chunk text with configured strategy
3. Generate embeddings for chunks
4. Store vectors in Qdrant
5. Optionally build knowledge graph in Neo4j
6. Store metadata in PostgreSQL

### Query Workflow
1. Embed user query
2. Retrieve similar chunks from vector store
3. Optionally traverse knowledge graph
4. Rerank results for relevance
5. Build context for LLM
6. Generate streaming response
7. Cache results

### Remove Document Workflow
1. Delete vectors from Qdrant
2. Remove graph nodes from Neo4j
3. Delete metadata from PostgreSQL
4. Clean up storage

## Testing Architecture

**Unit Tests** (`tests/unit/`):
- Domain logic testing
- Service layer testing
- Isolated component tests

**Integration Tests** (`tests/integration/`):
- Database integration
- Vector store integration
- LLM provider integration
- Workflow testing

**E2E Tests** (`tests/e2e/`):
- Complete CLI command testing
- Full RAG pipeline testing
- Multi-service integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `task check`
5. Run tests: `task test`
6. Submit a pull request

## License

GPL3.0

