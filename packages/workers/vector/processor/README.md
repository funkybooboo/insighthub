# Vector Processor Worker

Consolidated vector processing worker for embedding generation and vector indexing.

## Responsibility

- Consume `document.chunked` events
- Generate embeddings from text chunks using Sentence Transformers
- Store embeddings in Qdrant vector database
- Publish `document.indexed` events

## Processing Flow

```
+-----------------+
| document.chunked |
+-----------------+
         |
         v
+-----------------+     +-----------------+
|   Text Chunks   | --> |  Embedding Gen  |
|                 |     |                 |
| * Chunk 1       |     | * Sentence      |
| * Chunk 2       |     |   Transformers  |
| * Chunk N       |     | * Vectorization |
+-----------------+     +-----------------+
         |                        |
         |                        |
         v                        v
+-----------------+     +-----------------+
|   Embeddings    | --> |   Qdrant Store  |
|                 |     |                 |
| * Vector 1      |     | * Index         |
| * Vector 2      |     | * Metadata      |
| * Vector N      |     | * Search Ready  |
+-----------------+     +-----------------+
         |
         v
+-----------------+
| document.indexed |
+-----------------+
```

## Events

| Direction | Event              | Description                          |
|-----------|--------------------|--------------------------------------|
| Consumes  | document.chunked   | Triggered after document chunking    |
| Produces  | document.indexed   | Emitted after vector processing      |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
| QDRANT_URL         | http://qdrant:6333                                | Qdrant vector database |
| OLLAMA_BASE_URL    | http://ollama:11434                               | Ollama API endpoint    |
| WORKER_CONCURRENCY | 2                                                 | Concurrent processing  |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main

# Run tests
poetry run pytest tests/
```