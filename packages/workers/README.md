# Workers

This folder contains all the **workers** responsible for processing documents, embeddings, and graph structures in the InsightHub RAG system. Workers are **action-focused** and communicate via RabbitMQ events, allowing for **scalable, decoupled pipelines**.

The design supports:

- **User-uploaded documents**
- **External knowledge retrieval** (e.g., Wikipedia, URLs)
- **Vector-based RAG**
- **Graph-based RAG**
- **Hybrid RAG**
- **Large document handling** through chunking and streaming

---

## Worker List

| Worker      | Responsibility                                                   | Status      |
|-------------|------------------------------------------------------------------|-------------|
| `retriever` | Fetch external content from Wikipedia, URLs, or APIs             | [WIP] Partial  |
| `parser`    | Extract text/content from PDFs, DOCX, HTML, and TXT files        | [WIP] Partial  |
| `chucker`   | Split documents into smaller chunks for embeddings               | [WIP] Partial  |
| `embedder`  | Generate embeddings from document chunks                         | [WIP] Partial  |
| `indexer`   | Store embeddings into a vector database (Vector RAG)             | [WIP] Partial  |
| `connector` | Build graph nodes and edges in a graph database (Graph RAG)      | [TODO] Planned  |
| `enricher`  | Add metadata, summaries, classifications, or post-processing     | [TODO] Planned  |

---

## Worker Pipeline

### User-uploaded documents

```
user.upload -> parser -> chucker -> embedder -> indexer
                                                        \-> connector
                                                        \-> enricher
```

### External knowledge augmentation (Wikipedia, URL)

```
user.question -> retriever -> parser -> chucker -> embedder -> indexer
                                                                        \-> connector
                                                                        \-> enricher
```

> The `embedder` output is fanned out to both `indexer` (Vector RAG) and `connector` (Graph RAG).

---

## Event Flow (RabbitMQ)

| Event               | Produced By | Consumed By        |
|---------------------|-------------|--------------------|
| `document.uploaded` | user/system | parser             |
| `document.ingested` | parser      | chucker             |
| `document.parsed`   | parser      | chucker             |
| `document.chunked`  | chucker     | embedder           |
| `embedding.created` | embedder    | indexer, connector |
| `document.enriched` | enricher    | server (status)    |

Workers communicate exclusively via **events**, allowing multiple pipelines (Vector, Graph, or Hybrid) to run **in parallel and independently**.

---

## Design Principles

1. **Action-focused workers**: each worker performs a single, clear task.
2. **Source-agnostic**: works for both user uploads and external data.
3. **Scalable**: each worker can scale horizontally independently.
4. **RAG-agnostic**: same workers can support Vector RAG, Graph RAG, or Hybrid RAG.
5. **Large document support**: text is streamed, chunked, and processed incrementally to handle arbitrarily large files.

---

## Adding a New Worker

1. Create a new folder in `workers/` with the worker name (verb-style).
2. Implement the worker logic inside `main.py`.
3. Define input and output **RabbitMQ events** in line with the existing pipeline.
4. Add the worker to the orchestration system (Docker, Taskfile, etc.).

---

## Current Implementation Status

### Completed Workers [x]

- **Base Worker Infrastructure**: Common worker pattern with RabbitMQ integration
- **Event System**: Complete event schema definitions and handling
- **Error Handling**: Robust error handling and retry logic
- **Docker Integration**: All workers containerized and orchestrated

### Partially Implemented Workers [WIP]

- **Parser Worker**: PDF, DOCX, HTML, TXT parsing with Ollama integration
- **Chucker Worker**: Multiple chunking strategies (sentence, paragraph, character)
- **Embedder Worker**: Ollama embedding generation with batch processing
- **Indexer Worker**: Qdrant vector database integration
- **Retriever Worker**: Wikipedia and external content fetching

### Planned Workers [TODO]

- **Connector Worker**: Neo4j graph database construction
- **Enricher Worker**: Metadata enrichment and summarization

---

## Technology Stack

- **Language**: Python 3.11+ with Poetry
- **Messaging**: RabbitMQ with AMQP protocol
- **Vector Database**: Qdrant for similarity search
- **Graph Database**: Neo4j for graph operations
- **LLM Integration**: Ollama for local AI processing
- **Containerization**: Docker with health checks
- **Monitoring**: Structured logging with ELK integration

---

## Worker Pipeline Diagram

```
                 +------------+
                 |  Retriever |
                 | (Wikipedia,|
                 |  URLs, APIs)|
                 +-----+------+
                       |
                       v
                 +------------+
                 |  Parser    |
                 | (extract  |
                 |   text)    |
                 +-----+------+
                       |
                       v
                 +------------+
                 |  Chucker   |
                 | (split into|
                 |   chunks)  |
                 +-----+------+
                       |
                       v
                 +------------+
                 |  Embedder  |
                 | (create    |
                 | embeddings)|
                 +-----+------+
            +----------+----------+
            |                     |
            v                     v
     +------------+         +------------+
     |  Indexer   |         | Connector  |
     | (Vector DB)|         | (Graph DB) |
     +-----+------+         +-----+------+
            |                     |
            +----------+----------+
                       |
                       v
                 +------------+
                 |  Enricher  |
                 | (metadata, |
                 | summaries, |
                 | classify)  |
                 +------------+
```

---

## Configuration

Each worker can be configured via environment variables:

```bash
# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2

# Databases
QDRANT_HOST=localhost
QDRANT_PORT=6333
NEO4J_URI=bolt://localhost:7687
```

---

## Monitoring and Logging

All workers include:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: HTTP endpoints for monitoring
- **Metrics**: Processing time, queue depth, error rates
- **ELK Integration**: Logs shipped to Elasticsearch via Filebeat

---

## Notes

- All workers are **decoupled**; any downstream change will not affect upstream workers.
- Workers can be **added, removed, or replaced** independently.
- The pipeline supports **dynamic augmentation** of the knowledge base for both Vector and Graph RAG systems.
- Current implementation uses **Flask backend** with **RabbitMQ** for orchestration.
- Workers are designed to run in **Docker containers** with proper resource limits.

---

## Explanation

- **Retriever -> Parser**: Handles external content (Wikipedia, URLs) or uploaded files.
- **Parser -> Chucker -> Embedder**: Standard preprocessing pipeline for all content.
- **Embedder -> Indexer / Connector**: Branches for Vector RAG (`Indexer`) and Graph RAG (`Connector`).
- **Enricher**: Post-processing (metadata, summaries). Status updates are handled by the server via WebSocket.

This diagram shows how **both user-uploaded and external content** can feed **Vector and Graph RAG pipelines simultaneously**.