# InsightHub

A dual RAG system comparing Vector RAG and Graph RAG for academic research paper analysis.

## Features

* Vector RAG with document chunking, embedding, and retrieval
* Real-time streaming via Socket.IO WebSocket
* Fully local (Ollama + Qdrant + PostgreSQL)
* React frontend with chat interface
* Modular architecture with pluggable components
* Multiple LLM providers (Ollama, OpenAI, Claude, HuggingFace)
* CLI and REST API interfaces
* **Full application and infrastructure monitoring via ELK (Elasticsearch, Logstash, Kibana)**

## Tech Stack

**Frontend**: React 19 + TypeScript + Vite + TailwindCSS + Redux
**Backend**: Python 3.11 + Flask + SQLAlchemy + Socket.IO
**Infrastructure**: PostgreSQL, Qdrant, Ollama, MinIO, ELK Stack
**Tools**: Docker, Docker Compose, Poetry, Bun, Task

## Quick Start

### Prerequisites

* Docker & Docker Compose
* [Task](https://taskfile.dev): `sh -c "$(curl --location https://taskfile.dev/install.sh)"`
* 4GB disk space, 8GB RAM recommended

### Production

```bash
task build && task up
# Access: http://localhost:3000
# ELK Monitoring: http://localhost:5601
```

### Development

**Containerized (hot-reload)**:

```bash
task build-dev && task up-dev
# Server: http://localhost:5000
# Client: http://localhost:3000
# ELK Monitoring: http://localhost:5601
```

**Local + Infrastructure**:

```bash
task up-infra

# Terminal 1
cd packages/server && poetry install && task server

# Terminal 2
cd packages/client && bun install && task dev

# ELK Monitoring available at http://localhost:5601
```

---

## ELK Monitoring

The InsightHub application now ships logs from all project containers to the ELK stack:

* **Filebeat** reads container stdout/stderr logs.
* **Logstash** processes logs and forwards them to **Elasticsearch**.
* **Kibana** provides a web interface for searching, filtering, and visualizing logs.

**Default access**:

| Service       | URL                                            |
|---------------|------------------------------------------------|
| Kibana        | [http://localhost:5601](http://localhost:5601) |
| Elasticsearch | [http://localhost:9200](http://localhost:9200) |

**Tips**:

* You can filter logs in Kibana by `docker.container.name` or `docker.container.image`.
* Only containers labeled with `project=insighthub` are shipped to ELK.
* Use Kibana dashboards to separate app logs, database logs, and infrastructure logs.

---

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

---

## Project Structure

```
insighthub/
+-- packages/
|   +-- server/              # Python RAG backend
|   |   +-- src/
|   |   |   +-- infrastructure/rag/  # RAG implementations
|   |   |   +-- domains/             # Business logic
|   |   |   +-- api.py               # Flask app
|   |   +-- tests/           # Unit & integration tests
|   +-- client/              # React frontend
|       +-- src/
|           +-- components/  # UI components
|           +-- store/       # Redux state
+-- elk/                     # ELK stack configuration
|   +-- filebeat/filebeat.yml
|   +-- logstash/logstash.conf
+-- docker-compose.yml       # Service orchestration
+-- Taskfile.yml             # Task commands
```

---

## Testing

See [testing guide](docs/testing.md) for the complete testing guide.

### Quick Test Commands

```bash
# Client Tests
cd packages/client
task test              # Unit tests (319 passing)
task test:e2e          # E2E tests (Playwright)
task storybook         # Component documentation

# Server Tests
cd packages/server
task test              # Unit tests with coverage
task test:api          # Bruno API tests
```

---

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

---

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

---

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

# Check ELK logs
docker compose logs filebeat
docker compose logs logstash
docker compose logs kibana
```

See [docs/docker.md](docs/docker.md) for details.

---

## Documentation

* [Testing Guide](docs/testing.md) - Comprehensive testing documentation
* [Docker Setup](docs/docker.md)
* [Task Commands](docs/taskfile-setup.md)
* [Architecture](docs/architecture.md)
* [Contributing](docs/contributing.md)

## License

GPL-3.0
