# InsightHub

A dual RAG system comparing Vector RAG and Graph RAG for academic research paper analysis.

## Features

- Vector RAG with document chunking, embedding, and retrieval
- Real-time streaming via Socket.IO WebSocket
- Fully local (Ollama + Qdrant + PostgreSQL)
- React frontend with chat interface
- Modular architecture with pluggable components
- Multiple LLM providers (Ollama, OpenAI, Claude, HuggingFace)
- CLI and REST API interfaces

## Tech Stack

**Frontend**: React 19 + TypeScript + Vite + TailwindCSS + Redux
**Backend**: Python 3.11 + Flask + SQLAlchemy + Socket.IO
**Infrastructure**: PostgreSQL, Qdrant, Ollama, MinIO
**Tools**: Docker, Poetry, Bun, Task

## Quick Start

### Prerequisites

- Docker & Docker Compose
- [Task](https://taskfile.dev): `sh -c "$(curl --location https://taskfile.dev/install.sh)"`
- 4GB disk space, 8GB RAM recommended

### Production

```bash
task build && task up
# Access: http://localhost:3000
```

### Development

**Containerized (hot-reload)**:
```bash
task build-dev && task up-dev
# Server: http://localhost:5000
# Client: http://localhost:3000
```

**Local + Infrastructure**:
```bash
task up-infra

# Terminal 1
cd packages/server && poetry install && task server

# Terminal 2
cd packages/client && bun install && task dev
```

## Key Commands

```bash
task --list          # Show all commands
task up              # Start production
task up-dev          # Start development
task up-infra        # Infrastructure only
task down            # Stop all
task check           # Run quality checks
task logs-server-dev # View server logs
task clean           # Remove containers/volumes
```

## Project Structure

```
insighthub/
├── packages/
│   ├── server/              # Python RAG backend
│   │   ├── src/
│   │   │   ├── infrastructure/rag/  # RAG implementations
│   │   │   ├── domains/             # Business logic
│   │   │   └── api.py               # Flask app
│   │   └── tests/           # Unit & integration tests
│   └── client/              # React frontend
│       └── src/
│           ├── components/  # UI components
│           └── store/       # Redux state
├── docker-compose.yml       # Service orchestration
└── Taskfile.yml             # Task commands
```

## Code Quality

```bash
# Server
cd packages/server
task format      # Auto-format code
task test        # Run tests
task check       # All checks

# Client
cd packages/client
task format      # Prettier
task lint        # ESLint
task check       # All checks
```

## Configuration

Environment variables in `.env`:

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Database
DATABASE_URL=postgresql://insighthub:password@localhost:5432/insighthub

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://localhost:9000
```

## Troubleshooting

```bash
# Services not starting
task ps && task logs

# Database issues
task down && docker volume rm insighthub_postgres_data && task up-dev

# Port conflicts
lsof -i :5000 && lsof -i :3000

# Hot-reload not working
task restart-dev

# Pull models manually
docker compose exec ollama ollama pull llama3.2:1b
```

See [docs/docker.md](docs/docker.md) for details.

## Documentation

- [Docker Setup](docs/docker.md)
- [Task Commands](docs/taskfile-setup.md)
- [Architecture](docs/architecture.md)
- [Contributing](docs/contributing.md)

## License

GPL-3.0
