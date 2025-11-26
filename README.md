# InsightHub

A simplified RAG (Retrieval-Augmented Generation) system for querying documents using Vector similarity search.

## Architecture

- **Client**: React frontend with TailwindCSS
- **Server**: Flask API with Vector RAG
- **Databases**: PostgreSQL, Qdrant (vector DB)
- **LLM**: Local Ollama (llama3.2:1b + nomic-embed-text)

## Quick Start

```bash
# Start all services
docker compose up

# Or run locally for development
docker compose up postgres qdrant ollama ollama-setup
cd packages/server
poetry install
poetry run python -m src.database  # Initialize DB
poetry run python -m src.app       # Start server
```

The application will be available at:
- Client: http://localhost:5173
- API: http://localhost:5000
- Qdrant UI: http://localhost:6334

## Features

- Upload and parse documents (PDF, TXT)
- Automatic chunking and embedding
- Vector similarity search
- Chat interface with RAG retrieval
- Streaming LLM responses

## Project Structure

```
insighthub/
├── packages/
│   ├── client/              # React frontend
│   └── server/              # Flask API + RAG
│       └── src/
│           ├── models/      # Database models
│           ├── rag/         # RAG implementation
│           ├── llm/         # LLM providers
│           ├── embeddings/  # Embedding models
│           ├── storage/     # Vector store
│           ├── processing/  # Parsing & chunking
│           ├── routes/      # API endpoints
│           └── services/    # Business logic
└── docker-compose.yml
```

## API Endpoints

### Documents
- `POST /api/documents` - Upload document
- `GET /api/documents` - List all documents
- `GET /api/documents/<id>` - Get document details
- `DELETE /api/documents/<id>` - Delete document

### Chat
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - List sessions
- `GET /api/chat/sessions/<id>/messages` - Get messages
- `POST /api/chat/sessions/<id>/messages` - Send message (supports streaming)

### Health
- `GET /api/health` - Health check

## Development

### Server
```bash
cd packages/server
poetry install
poetry run python -m src.app

# Run tests
poetry run pytest

# Format code
poetry run black src
poetry run isort src
poetry run ruff check src
```

### Client
```bash
cd packages/client
bun install
bun run dev

# Run tests
bun run test

# Format code
bun run format
```

## Configuration

Environment variables (see `packages/server/src/config.py`):
- `DATABASE_URL` - PostgreSQL connection string
- `QDRANT_HOST` / `QDRANT_PORT` - Vector database
- `OLLAMA_BASE_URL` - LLM API endpoint
- `SECRET_KEY` - Flask secret key

## Technology Stack

**Backend:**
- Python 3.11+
- Flask web framework
- SQLAlchemy ORM
- Qdrant vector database
- Sentence Transformers for embeddings
- Ollama for LLM

**Frontend:**
- React 19
- TypeScript
- TailwindCSS
- Vite
- React Router
- Axios

## License

MIT

## Refactoring Notes

This is a simplified version of InsightHub that removes the complex microservices architecture. See `REFACTOR.md` for details on what changed and why.

Previous architecture had:
- 13+ worker services
- RabbitMQ message queue
- Complex event-driven system
- Multi-tenancy (workspaces)

Current architecture has:
- Single Python server
- Direct function calls
- Simplified single-user system
- Same RAG functionality
