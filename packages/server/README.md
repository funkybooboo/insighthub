# InsightHub Server

Flask backend for InsightHub dual RAG system, providing REST API and WebSocket endpoints for document processing, chat interactions, and workspace management with clean architecture principles.

## Features

### Core Architecture
- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Dual RAG System**: Vector RAG with Qdrant and Graph RAG (planned) with Neo4j
- **Multi-LLM Support**: Ollama (local), OpenAI, Claude, HuggingFace integration
- **Real-time Communication**: WebSocket support via Flask-SocketIO
- **Asynchronous Processing**: RabbitMQ message queue for background jobs

### API & Communication
- **REST API**: Comprehensive RESTful endpoints for all operations
- **WebSocket Events**: Real-time streaming for chat and status updates
- **JWT Authentication**: Secure token-based authentication and authorization
- **Input Validation**: Comprehensive request validation and sanitization
- **Rate Limiting**: Configurable rate limiting per endpoint and user

### Document Processing
- **Document Pipeline**: Parser -> Chunker -> Embedder -> Indexer workflow
- **Multiple Formats**: PDF and text document support
- **Background Processing**: Asynchronous document processing with status updates
- **Blob Storage**: MinIO/S3 compatible file storage
- **Error Handling**: Comprehensive error tracking and recovery

### Data Management
- **PostgreSQL**: Primary database for application data
- **Vector Database**: Qdrant for similarity search and storage
- **Migrations**: Version-controlled database schema management
- **Repository Pattern**: Abstracted data access with clean interfaces

### Security & Monitoring
- **Security Headers**: X-Frame-Options, CSP, CORS configuration
- **Middleware Stack**: Security, logging, rate limiting, monitoring
- **Health Checks**: Comprehensive health check endpoints
- **Structured Logging**: JSON logging with correlation IDs

## Tech Stack

### Core Framework
- **Python 3.11+** with modern type hints
- **Flask 3.0+** as web framework
- **Flask-SocketIO** for WebSocket support
- **Flask-JWT-Extended** for authentication

### Database & Storage
- **PostgreSQL 16** for primary data storage
- **Qdrant** for vector storage and similarity search
- **MinIO/S3** for blob storage
- **RabbitMQ** for message queuing

### RAG & AI
- **Ollama** for local LLM inference
- **OpenAI** API integration
- **Anthropic Claude** API integration
- **Sentence Transformers** for embeddings
- **PyPDF** for document parsing

### Development & Testing
- **Poetry** for dependency management
- **Pytest** for testing framework
- **Black** for code formatting
- **Ruff** for linting and code quality
- **MyPy** for static type checking

## Development Setup

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- PostgreSQL, Qdrant, RabbitMQ (or use Docker)

### Installation

```bash
cd packages/server

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Copy and configure environment file
cp .env.example .env
# Edit .env with your configuration
```

### Environment Configuration

Key environment variables:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://insighthub:password@localhost:5432/insighthub

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=insighthub

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=insighthub-documents

# Message Queue
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Running Server

```bash
# Development server with hot reload
poetry run python -m src.api

# Or using Task
task server          # Start development server
task server:prod     # Start production server
task server:debug    # Start with debug mode
```

The server will start at `http://localhost:5000`.

### Available Scripts

```bash
# Development
task server          # Start development server
task server:prod     # Start production server
task server:debug     # Start with debug mode
task shell           # Start interactive shell

# Database
task db:migrate      # Run database migrations
task db:reset        # Reset database
task db:seed         # Seed database with sample data

# Code Quality
task format          # Format code with Black and isort
task lint            # Run Ruff linter
task typecheck       # Run MyPy type checking
task check           # Run all quality checks

# Testing
task test            # Run all tests
task test:unit       # Run unit tests only
task test:integration # Run integration tests only
task test:coverage   # Run tests with coverage
task test:api        # Run API tests (Bruno)

# Documentation
task docs:serve      # Serve API documentation
task docs:generate   # Generate OpenAPI documentation
```

## Project Structure

```
packages/server/
--- src/
|   --- domains/                 # Business logic by domain
|   |   --- auth/               # Authentication domain
|   |   |   --- routes.py       # Auth API routes
|   |   |   --- service.py      # Auth business logic
|   |   |   --- dtos.py         # Data transfer objects
|   |   |   --- exceptions.py   # Domain exceptions
|   |   --- chat/               # Chat domain
|   |   |   --- routes.py       # Chat API routes
|   |   |   --- service.py      # Chat business logic
|   |   |   --- socket_handlers.py # WebSocket handlers
|   |   |   --- dtos.py         # Data transfer objects
|   |   |   --- mappers.py      # Data mapping
|   |   |   --- exceptions.py   # Domain exceptions
|   |   --- documents/          # Document management
|   |   |   --- routes.py       # Document API routes
|   |   |   --- service.py      # Document business logic
|   |   |   --- dtos.py         # Data transfer objects
|   |   |   --- mappers.py      # Data mapping
|   |   |   --- exceptions.py   # Domain exceptions
|   |   --- workspaces/         # Workspace management
|   |   |   --- routes.py       # Workspace API routes
|   |   |   --- service.py      # Workspace business logic
|   |   |   --- dtos.py         # Data transfer objects
|   |   |   --- mappers.py      # Data mapping
|   |   |   --- exceptions.py   # Domain exceptions
|   |   --- users/              # User management
|   |   |   --- service.py      # User business logic
|   |   |   --- mappers.py      # Data mapping
|   |   |   --- exceptions.py   # Domain exceptions
|   |   --- health/             # Health checks
|   |   |   --- routes.py       # Health check endpoints
|   |   --- status/             # Status updates
|   |       --- socket_handlers.py # Status WebSocket handlers
|   --- infrastructure/          # External integrations
|   |   --- auth/               # Authentication infrastructure
|   |   |   --- jwt_utils.py    # JWT utilities
|   |   |   --- middleware.py   # Auth middleware
|   |   --- database/           # Database infrastructure
|   |   |   --- __init__.py
|   |   --- middleware/         # HTTP middleware
|   |   |   --- security.py     # Security headers
|   |   |   --- logging.py      # Request logging
|   |   |   --- rate_limiting.py # Rate limiting
|   |   |   --- validation.py   # Request validation
|   |   |   --- monitoring.py   # Metrics and monitoring
|   |   --- socket/             # WebSocket infrastructure
|   |   |   --- socket_handler.py # Base socket handler
|   |   |   --- __init__.py
|   |   --- rag/                # RAG system implementations
|   |       --- rag.py          # RAG interface
|   |       --- vector_rag.py    # Vector RAG implementation
|   |       --- factory.py      # RAG factory
|   |       --- chunking/       # Text chunking strategies
|   |       --- embeddings/      # Embedding models
|   |       --- vector_stores/  # Vector store implementations
|   --- api.py                  # Main Flask application
|   --- config.py               # Application configuration
|   --- context.py              # Application context
--- tests/                      # Test suite
|   --- unit/                   # Unit tests
|   |   --- test_*.py          # Unit test files
|   |   --- conftest.py        # Unit test configuration
|   --- integration/            # Integration tests
|   |   --- test_*.py          # Integration test files
|   |   --- conftest.py        # Integration test configuration
|   --- config.py               # Test configuration
|   --- conftest.py             # Global test configuration
|   --- context.py              # Test context
--- migrations/                 # Database migrations
|   --- 001_initial_schema.sql
|   --- 002_add_missing_schema.sql
|   --- migrate.py             # Migration utility
--- docs/                       # API documentation
|   --- api.md                  # API documentation
|   --- configuration.md        # Configuration guide
|   --- database.md             # Database documentation
|   --- middleware.md           # Middleware documentation
|   --- quick-start.md          # Quick start guide
|   --- testing.md              # Testing documentation
--- bruno/                      # API testing (Bruno)
|   --- Auth/                   # Auth API tests
|   --- Chat/                   # Chat API tests
|   --- Documents/              # Document API tests
|   --- Workspaces/             # Workspace API tests
|   --- Health/                 # Health check tests
--- pyproject.toml              # Poetry configuration
--- poetry.lock                 # Dependency lock file
--- Taskfile.yml                # Task automation
--- Dockerfile                  # Docker configuration
--- openapi.yaml                # OpenAPI specification
--- README.md                   # This file
```

## Architecture Overview

### Clean Architecture Layers

```
+-------------------------------------------------------------+
|                    Presentation Layer                      |
|  (API Routes + WebSocket Handlers + Middleware)            |
--------------------------------------------------------------+
|                      Domain Layer                          |
|     (Business Logic + Domain Models + Use Cases)          |
--------------------------------------------------------------+
|                 Infrastructure Layer                        |
|  (Database + External APIs + RAG System + Storage)         |
--------------------------------------------------------------+
```

### Domain-Driven Design

Each domain follows the same structure:
- **routes.py**: API endpoints and request handling
- **service.py**: Business logic and use cases
- **dtos.py**: Data transfer objects for API communication
- **mappers.py**: Data mapping between layers
- **exceptions.py**: Domain-specific exceptions

### Key Patterns

**Repository Pattern**: Abstract data access with clean interfaces
**Service Layer**: Encapsulates business logic and use cases
**Dependency Injection**: Components receive dependencies via constructors
**Factory Pattern**: Creates RAG instances with pluggable components

## API Documentation

### Authentication Endpoints

```bash
POST /api/auth/login          # User login
POST /api/auth/signup         # User registration
POST /api/auth/logout         # User logout
GET  /api/auth/me            # Get current user
PATCH /api/auth/profile       # Update profile
PATCH /api/auth/preferences   # Update preferences
POST /api/auth/change-password # Change password
GET  /api/auth/default-rag-config # Get default RAG config
PUT  /api/auth/default-rag-config # Save default RAG config
```

### Workspace Endpoints

```bash
GET    /api/workspaces                    # List workspaces
POST   /api/workspaces                    # Create workspace
GET    /api/workspaces/{id}               # Get workspace details
PATCH  /api/workspaces/{id}               # Update workspace
DELETE /api/workspaces/{id}               # Delete workspace
GET    /api/workspaces/{id}/rag-config    # Get RAG config
POST   /api/workspaces/{id}/rag-config    # Create RAG config
PATCH  /api/workspaces/{id}/rag-config    # Update RAG config
```

### Document Endpoints

```bash
POST /api/workspaces/{id}/documents/upload    # Upload document
GET  /api/workspaces/{id}/documents           # List documents
DELETE /api/workspaces/{id}/documents/{doc_id} # Delete document
POST /api/workspaces/{id}/documents/fetch-wikipedia # Fetch Wikipedia
```

### Chat Endpoints

```bash
POST /api/workspaces/{id}/chat/sessions/{session_id}/messages # Send message
POST /api/workspaces/{id}/chat/sessions/{session_id}/cancel   # Cancel message
```

### WebSocket Events

**Client to Server**:
- `chat_message`: Send chat message
- `cancel_message`: Cancel streaming response

**Server to Client**:
- `chat_chunk`: Streaming response token
- `chat_complete`: Response completion
- `chat_cancelled`: Response cancelled
- `document_status`: Document processing updates
- `workspace_status`: Workspace status updates
- `wikipedia_fetch_status`: Wikipedia fetch progress

## RAG System

### Vector RAG Implementation

```python
from src.infrastructure.rag.factory import create_rag

# Create Vector RAG instance
rag = create_rag(
    rag_type="vector",
    chunking_strategy="sentence",
    embedding_type="ollama",
    vector_store_type="qdrant",
    chunk_size=1000,
    chunk_overlap=200,
    top_k=8
)

# Add documents
rag.add_documents([
    {"text": "Document content...", "metadata": {"source": "paper.pdf"}}
])

# Query with RAG
response = rag.query(
    query="What is the main contribution?",
    llm_generator="ollama"
)
```

### Supported Components

**Chunking Strategies**:
- Character-based chunking
- Sentence-based chunking
- Word-based chunking

**Embedding Models**:
- Ollama embeddings (local)
- OpenAI embeddings
- Sentence Transformers

**Vector Stores**:
- Qdrant (production)
- In-memory (testing)

## Testing

### Test Structure

```bash
tests/
--- unit/                   # Unit tests with dummy implementations
--- integration/            # Integration tests with testcontainers
--- config.py              # Test configuration
--- conftest.py            # Global test setup
--- context.py             # Test context
```

### Running Tests

```bash
# All tests
task test

# Unit tests only
task test:unit

# Integration tests only
task test:integration

# With coverage
task test:coverage

# API tests (Bruno)
task test:api
```

### Testing Philosophy

**Unit Tests**: Use dummy implementations, not mocks
- Test components in isolation
- Fast execution (< 100ms per test)
- Real objects with minimal logic

**Integration Tests**: Use testcontainers
- Test real component interactions
- Temporary Docker containers
- Clean slate per test

## Database

### Migrations

```bash
# Run pending migrations
task db:migrate

# Reset database (dangerous)
task db:reset

# Create new migration
# Create SQL file in migrations/ directory
# Follow naming convention: 003_description.sql
```

### Schema

Key tables:
- `users`: User accounts and profiles
- `workspaces`: Workspace definitions
- `workspace_rag_configs`: RAG configurations
- `documents`: Document metadata
- `chat_sessions`: Chat session data
- `chat_messages`: Chat message history

## Security

### Authentication
- JWT-based authentication
- Secure password hashing with bcrypt
- Token expiration and refresh
- Session management

### Authorization
- User-scoped resource access
- Workspace ownership validation
- API endpoint protection

### Security Headers
- X-Frame-Options
- X-Content-Type-Options
- Content Security Policy
- CORS configuration

### Input Validation
- Request size limits
- Path traversal prevention
- SQL injection protection
- XSS prevention

## Performance

### Caching
- Vector embeddings in Qdrant
- Database connection pooling
- HTTP connection reuse

### Optimization
- Batch processing for embeddings
- Streaming responses for chat
- Efficient document chunking
- Background job processing

## Monitoring

### Health Checks

```bash
GET /health              # Basic health check
GET /health/heartbeat    # Detailed health status
GET /health/database     # Database connectivity
GET /health/queue        # Message queue status
```

### Logging
- Structured JSON logging
- Correlation ID tracking
- Request/response logging
- Error stack traces

### Metrics
- Request rate and latency
- Error rates by endpoint
- Database query performance
- RAG system statistics

## Docker Integration

```bash
# Build image
docker build -t insighthub-server .

# Run with Docker Compose
docker compose up server

# Development with hot reload
docker compose up server-dev
```

### Docker Features
- Multi-stage builds
- Health checks
- Graceful shutdown
- Volume mounting for development

## Configuration

### Environment Variables

See "Environment Configuration" section above for complete list.

### Configuration Management

- `config.py`: Application configuration
- Environment-specific settings
- Default values and validation
- Configuration schema

## Troubleshooting

### Common Issues

```bash
# Database connection issues
task db:reset

# Port conflicts
lsof -i :5000

# Import errors
poetry install --no-dev

# Test failures
task test:unit  # Run unit tests only
task test:integration  # Run integration tests only
```

### Debug Mode

```bash
# Start with debug mode
task server:debug

# Enable debug logging
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

## Contributing

1. Follow clean architecture principles
2. Add type hints for all functions
3. Write tests for new features
4. Update documentation
5. Run code quality checks before committing
6. Use conventional commit messages