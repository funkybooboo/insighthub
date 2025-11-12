# InsightHub

A dual RAG (Retrieval-Augmented Generation) system for academic research paper analysis, comparing Vector RAG and Graph RAG approaches.

**Core Goal**: Enable users to query academic papers and Wikipedia content through an AI chatbot, comparing Vector RAG vs Graph RAG performance.

## Features

- **Dual RAG Implementation**: Compare Vector RAG and Graph RAG approaches
- **Real-time Streaming**: Token-by-token LLM response streaming via WebSocket
- **Fully Local**: Runs entirely on your machine using Docker (Ollama + Qdrant)
- **React Frontend**: Modern chatbot interface with conversational memory
- **Modular Architecture**: Pluggable components (embeddings, chunking, vector stores)
- **Multiple Chunking Strategies**: Character, sentence, and word-based options
- **Graph RAG**: Entity extraction and community detection (in development)

## Architecture

The system follows a modular RAG pipeline:

1. **Ingestion**: Documents -> Chunker -> Chunks with metadata
2. **Embedding**: Chunks -> Ollama (nomic-embed-text) -> Vectors
3. **Storage**: Vectors -> Qdrant (Vector) or Neo4j (Graph)
4. **Retrieval**: Query -> Similarity/Graph Search -> Top-K results
5. **Generation**: Query + Context -> Ollama (llama3.2) -> Answer

## Tech Stack

**Frontend**: React 19 + TypeScript + Vite + TailwindCSS + Redux Toolkit

**Backend**: Python 3.11+ with Flask + Socket.IO
- **Vector RAG**: Qdrant + Ollama (nomic-embed-text + llama3.2)
- **Graph RAG**: Neo4j + Leiden clustering (in development)
- **Chunking**: Character, sentence, and word-based strategies

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ and Bun (for frontend development)
- Python 3.11+ (for backend development)
- ~4GB disk space for models
- ~8GB RAM recommended

### Running the Full System

```bash
docker-compose up
```

This will start all services (Ollama, Qdrant, Neo4j, backend, frontend) and automatically pull required models. First run takes ~5 minutes to download models (2.5GB).

### Development Setup

**Backend**:
```bash
cd packages/server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Frontend**:
```bash
cd packages/client
bun install && bun run dev
```

**Services**:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Qdrant**: http://localhost:6333 (UI: http://localhost:6334)
- **Ollama**: http://localhost:11434
- **Jupyter**: http://localhost:8888 (run: `docker-compose --profile dev up jupyter`)

## Usage Example

```python
from src.infrastructure.rag.factory import create_rag

# Create RAG instance
rag = create_rag({
    "rag_type": "vector",
    "chunking_strategy": "sentence",
    "embedding_type": "ollama",
    "vector_store_type": "qdrant",
    "ollama_base_url": "http://localhost:11434",
    "chunk_size": 500,
    "chunk_overlap": 50
})
```

See `packages/server/src/main.py` for a complete demo.

## Project Structure

```
insighthub/
├── packages/
│   ├── client/              # React frontend (Vite + TypeScript)
│   │   └── src/
│   │       ├── components/  # UI components
│   │       ├── lib/         # Utilities
│   │       └── store/       # Redux state
│   └── server/              # Python RAG backend
│       ├── src/
│       │   ├── infrastructure/rag/  # RAG implementations and components
│       │   │   ├── chunking/        # Chunking strategies
│       │   │   ├── embeddings/      # Embedding models (ollama, openai)
│       │   │   ├── vector_stores/   # Vector stores (qdrant, in_memory)
│       │   │   ├── factory.py       # RAG factory
│       │   │   └── rag.py           # Base RAG interface
│       │   ├── domains/             # Domain logic (chat, documents, auth)
│       │   └── infrastructure/      # Infrastructure services
│       └── tests/           # Unit and integration tests
├── docs/                    # Documentation
├── docker-compose.yml       # Service orchestration
└── Makefile                 # Development commands
```

## Code Quality

**Python** (packages/server/):
```bash
make check       # Run all checks (format, lint, type-check, test)
make format      # Format code (black + isort)
pytest -v        # Run tests
```

**TypeScript** (packages/client/):
```bash
bun run format   # Format code (prettier)
bun run lint     # ESLint
bun test         # Run tests
```

**GitHub Actions** (CI/CD):
- All PRs must pass formatting, linting, type-checking, and tests
- Run workflows locally with `act` (see [docs/github-actions.md](docs/github-actions.md))

## Configuration

Copy `packages/server/.env.example` to `.env` and configure:

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50
CHUNK_STRATEGY=sentence

# RAG
RAG_TOP_K=5
```

## Development Status

**Phase 1: Vector RAG** - Complete
- Modular architecture with dependency injection
- Multiple chunking strategies (character, sentence, word)
- Ollama + Qdrant integration

**Phase 2: Graph RAG + Frontend** - In Progress
- Neo4j integration and Leiden clustering
- React chatbot with conversational memory (Mem0)
- Vector vs Graph RAG comparison framework

**Phase 3: Advanced Features** - Planned
- Hybrid search, evaluation metrics, PDF parsing

## Vector RAG vs Graph RAG

| Aspect | Vector RAG | Graph RAG |
|--------|------------|-----------|
| **Retrieval** | Similarity search | Graph traversal + clustering |
| **Context** | Fixed chunks | Entity relationships |
| **Best For** | Factual retrieval | Complex reasoning |
| **Speed** | Fast | Slower |

## Troubleshooting

**Ollama connection refused**: `docker-compose restart ollama`

**Model not found**:
```bash
docker exec ollama ollama pull nomic-embed-text
docker exec ollama ollama pull llama3.2
```

**Port already in use**: `lsof -i :8000` then `kill -9 <PID>`

**Module not found**:
```bash
cd packages/client && bun install
cd packages/server && pip install -r requirements.txt
```

## License

GPL License
