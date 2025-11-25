# Vector Query Worker

Vector-based retrieval worker for similarity search queries.

## Responsibility

- Consume `chat.vector_query` events for vector-based retrieval
- Generate embeddings for user queries
- Perform similarity search against vector database
- Return relevant context for LLM generation
- Publish `chat.vector_query_completed` or `chat.vector_query_failed` events

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | chat.vector_query          | Triggered for vector-based queries   |
| Produces  | chat.vector_query_completed | Emitted with vector search results   |
| Produces  | chat.vector_query_failed   | Emitted on query errors              |

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