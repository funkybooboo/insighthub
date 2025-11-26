# InsightHub

A comprehensive dual RAG (Retrieval-Augmented Generation) system comparing Vector RAG and Graph RAG approaches for academic research paper analysis with real-time chat interface and workspace management.

## Features

### Core RAG System
- **Dual RAG Implementation**: Vector RAG with Qdrant and Graph RAG (planned) with Neo4j
- **Multiple LLM Providers**: Ollama (local), OpenAI, Claude, HuggingFace
- **Document Processing**: PDF and text document parsing, chunking, and embedding
- **Real-time Streaming**: Token-by-token LLM responses via WebSocket
- **Intelligent Enhancement**: Wikipedia fetch integration for improved context

### User Interface & Experience
- **Workspace Management**: Isolated environments with custom RAG configurations
- **Real-time Chat**: WebSocket-based streaming with conversation memory
- **Document Management**: Upload, track processing status, and organize documents
- **User Authentication**: Secure JWT-based login/signup with profile management
- **Theme Support**: Light/dark mode with user preferences
- **Responsive Design**: Mobile-friendly interface built with TailwindCSS

### Infrastructure & Monitoring
- **ELK Stack**: Full application monitoring with Elasticsearch, Logstash, and Kibana
- **Docker Compose**: Complete containerized deployment
- **Message Queue**: RabbitMQ for asynchronous document processing
- **Blob Storage**: MinIO/S3 compatible file storage
- **Health Checks**: Comprehensive system health monitoring

## Architecture

InsightHub follows clean architecture principles with clear separation of concerns:

```
+-------------------------------------------------------------+
|                    Presentation Layer                      |
|  (React Frontend + Flask API Routes + WebSocket Handlers)   |
--------------------------------------------------------------+
|                      Domain Layer                          |
|     (Business Logic Services + Domain Models)              |
--------------------------------------------------------------+
|                 Infrastructure Layer                        |
|  (RAG Engine + Database + Storage + LLM Providers)        |
--------------------------------------------------------------+
```

### Key Components

1. **React Frontend** (`packages/client/`)
   - React 19 + TypeScript + Vite
   - Redux Toolkit for state management
   - Socket.IO for real-time communication
   - TailwindCSS for styling

2. **Flask Backend** (`packages/server/`)
   - Python 3.11+ with Flask-SocketIO
   - Clean architecture with domain-driven design
   - JWT authentication and authorization
   - REST API with WebSocket support

3. **RAG Engine** (`packages/server/src/infrastructure/rag/`)
   - Pluggable Vector and Graph RAG implementations
   - Multiple embedding models and vector stores
   - Configurable chunking strategies

4. **Worker Services** (`packages/workers/`)
   - Document processing pipeline (parser, chunker, embedder, indexer)
   - Asynchronous processing with RabbitMQ
   - Real-time status updates

5. **Infrastructure**
   - PostgreSQL for application data
   - Qdrant for vector storage
   - MinIO for blob storage
   - ELK stack for monitoring

## Quick Start

### Prerequisites

- Docker & Docker Compose
- [Task](https://taskfile.dev): `sh -c "$(curl --location https://taskfile.dev/install.sh)"`
- 4GB disk space, 8GB RAM recommended

### Production Deployment

```bash
# Build and start all services
task build && task up

# Access the application
# Frontend: http://localhost:3000
# ELK Monitoring: http://localhost:5601
```

### Development Environment

**Option 1: Containerized Development (Recommended)**
```bash
# Start development services with hot reload
task build-dev && task up-dev

# Services:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# ELK Monitoring: http://localhost:5601
```

**Option 2: Local Development with Infrastructure**
```bash
# Start infrastructure services only
task up-infra

# Install Python workspace dependencies (one-time setup)
./install-python-workspace.sh

# Terminal 1: Start backend server
cd packages/server
poetry run python -m src.api

# Terminal 2: Start frontend
cd packages/client
bun install && bun run dev
```

## Application Workflow

### 1. User Authentication & Setup
- Users create accounts or sign in with existing credentials
- Configure default RAG preferences (embedding models, chunking parameters)
- Set theme and profile preferences

### 2. Workspace Creation & Configuration
- Create isolated workspaces for different research topics
- Configure RAG settings per workspace (Vector/Graph RAG, models, parameters)
- Real-time provisioning status updates via WebSocket

### 3. Document Upload & Processing
- Upload PDF/text documents to specific workspaces
- Automatic processing pipeline: parsing -> chunking -> embedding -> indexing
- Real-time status tracking for each processing stage
- Chat functionality locked until documents are fully processed

### 4. Interactive Chat with RAG
- Query documents with intelligent context retrieval
- Receive streaming responses with source attribution
- Automatic RAG enhancement when context is insufficient:
  - Upload additional documents
  - Fetch relevant Wikipedia content
  - Continue without additional context

### 5. Workspace Management
- Delete workspaces with complete resource cleanup
- Monitor workspace and document processing status
- Switch between active workspaces seamlessly

## Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for development and building
- **Redux Toolkit** for state management
- **TailwindCSS** for styling
- **Socket.IO Client** for real-time communication
- **Vitest** for testing

### Backend
- **Python 3.11+** with Flask
- **Flask-SocketIO** for WebSocket support
- **PostgreSQL** for data persistence
- **Qdrant** for vector storage
- **RabbitMQ** for message queuing
- **Poetry** for dependency management

### Infrastructure
- **Docker** & **Docker Compose** for containerization
- **MinIO** for blob storage
- **ELK Stack** for monitoring and logging
- **Ollama** for local LLM inference
- **GitHub Actions** for CI/CD

## Key Commands

```bash
# Task Management
task --list          # Show all available commands
task up              # Start production services
task up-dev          # Start development services
task up-infra        # Start infrastructure only
task down            # Stop all services
task restart         # Restart development services
task clean           # Remove containers and volumes

# Code Quality
task check           # Run all quality checks
task format          # Format code (Black + Prettier)
task lint            # Run linters (Ruff + ESLint)
task test            # Run all tests
task test:coverage   # Run tests with coverage

# Development
task logs            # View service logs
task logs-dev        # View development logs
task shell           # Access development shell
task ps              # Show running services
```

## Project Structure

```
insighthub/
--- packages/
|   --- client/                 # React frontend application
|   |   --- src/
|   |   |   --- components/     # React components
|   |   |   --- pages/          # Page components
|   |   |   --- services/       # API and WebSocket services
|   |   |   --- store/          # Redux state management
|   |   |   --- types/          # TypeScript definitions
|   |   --- package.json
|   --- server/                 # Flask backend application
|   |   --- src/
|   |   |   --- domains/        # Business logic by domain
|   |   |   --- infrastructure/ # External integrations
|   |   |   --- api.py          # Flask application
|   |   --- tests/              # Unit and integration tests
|   |   --- pyproject.toml
|   --- cli/                    # Command-line interface
|   --- workers/                # Background processing workers
|   |   --- general/            # General purpose workers
|   |   |   --- chat/           # Chat orchestration worker
|   |   |   --- chunker/        # Text chunking worker
|   |   |   --- enricher/       # Document enrichment worker
|   |   |   --- parser/         # Document parsing worker
|   |   |   --- router/         # Document routing worker
|   |   |   --- wikipedia/      # Wikipedia fetch worker
|   |   |   --- infrastructure-manager/  # Workspace provisioning
|   |   --- vector/             # Vector RAG workers
|   |   |   --- processor/      # Vector embedding and indexing
|   |   |   --- query/          # Vector similarity search
|   |   --- graph/              # Graph RAG workers (planned)
|   |   |   --- connector/      # Graph node connection
|   |   |   --- construction/   # Graph building
|   |   |   --- preprocessor/   # Entity extraction
|   |   |   --- query/          # Graph traversal queries
|   --- shared/                 # Shared libraries
|   |   --- python/             # Shared Python package (shared-python)
|   |   --- typescript/         # Shared TypeScript package
--- docs/                       # Documentation
--- elk/                        # ELK stack configuration
--- .github/workflows/          # CI/CD workflows
--- docker-compose.yml          # Service orchestration
--- Taskfile.yml                # Task automation
--- install-python-workspace.sh # Python workspace installer
--- README.md
```

### Workspace Architecture

InsightHub uses a **monorepo workspace structure** for dependency management:

- **TypeScript**: Bun workspaces with shared-typescript for client and CLI
- **Python**: Poetry path dependencies with shared-python for server and workers
- **Benefits**: No duplicate dependencies, editable installs, instant code changes

All packages (server + 14 workers) share common dependencies from `packages/shared/python`. Changes to shared code are immediately available without rebuilds.

See [Python Workspace Guide](docs/setup/python-workspace.md) for setup details.

## Testing

### Client Testing
```bash
cd packages/client
task test              # Run unit tests (438 tests passing)
task test:coverage     # Run with coverage report
task test:e2e          # Run E2E tests (Playwright)
task storybook         # View component documentation
```

### Server Testing
```bash
cd packages/server
task test              # Run unit and integration tests
task test:coverage     # Run with coverage report
task test:api          # Run API tests (Bruno)
```

### Test Coverage
- **Client**: 438 tests across components, services, and utilities
- **Server**: Comprehensive unit and integration test coverage
- **E2E**: Playwright tests for critical user flows
- **API**: Bruno tests for all REST endpoints

## Configuration

### Environment Variables
Key environment variables for configuration:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Database
DATABASE_URL=postgresql://insighthub:password@localhost:5432/insighthub

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# Application
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Monitoring & Logging

### ELK Stack Integration
- **Elasticsearch**: Log storage and search
- **Logstash**: Log processing and enrichment
- **Kibana**: Log visualization and dashboards

**Access Points**:
- Kibana Dashboard: http://localhost:5601
- Elasticsearch API: http://localhost:9200

**Features**:
- Container log aggregation
- Structured logging with correlation IDs
- Real-time log streaming
- Custom dashboards for different services

## Troubleshooting

### Common Issues

```bash
# Services not starting
task ps && task logs

# Database connection issues
task down && docker volume rm insighthub_postgres_data && task up-dev

# Port conflicts
lsof -i :3000 && lsof -i :5000

# Hot-reload not working
task restart-dev

# Model download issues
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text

# ELK logging issues
docker compose logs filebeat logstash kibana
```

### Performance Optimization
- Use SSD storage for better database performance
- Allocate sufficient RAM for Ollama models
- Monitor resource usage via Kibana dashboards
- Configure appropriate chunk sizes for document processing

## Documentation

### Setup & Installation
- [Docker Setup](docs/setup/docker.md) - Container deployment guide
- [Python Workspace](docs/setup/python-workspace.md) - Python monorepo workspace setup
- [Docker Workspace Update](docs/setup/docker-workspace-update.md) - Docker workspace changes
- [Taskfile Setup](docs/setup/taskfile-setup.md) - Task automation configuration

### Architecture
- [System Architecture](docs/architecture/architecture.md) - Detailed system architecture
- [Project Structure](docs/architecture/project-structure.md) - Codebase organization
- [RAG System](docs/architecture/rag-system-documentation.md) - RAG implementation details
- [Streaming](docs/architecture/streaming.md) - Real-time streaming architecture

### Development
- [Contributing Guide](docs/development/contributing.md) - Development guidelines
- [Testing Guide](docs/development/testing.md) - Comprehensive testing documentation
- [GitHub Actions](docs/development/github-actions.md) - CI/CD workflows

### User Guides
- [Client User Flows](docs/user-guides/client-user-flows.md) - Detailed user interaction flows

### Additional Resources
- [API Documentation](packages/server/docs/api.md) - REST API reference
- [CHANGELOG](CHANGELOG.md) - Version history and changes
- [CLAUDE.md](CLAUDE.md) - Claude AI assistant instructions
- [GEMINI.md](GEMINI.md) - Gemini AI assistant instructions

## License

GPL-3.0 - See [LICENSE](LICENSE) file for details.