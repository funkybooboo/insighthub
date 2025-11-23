# Indexer Worker

Vector indexer worker - stores embeddings in Qdrant vector database.

## Responsibility

- Consume embedding.created events
- Upsert vectors to Qdrant with metadata
- Publish vector.indexed events

## Events

| Direction | Event             | Description                          |
|-----------|-------------------|--------------------------------------|
| Consumes  | embedding.created | Triggered when embeddings are ready  |
| Produces  | vector.indexed    | Emitted after vectors are stored     |

## Environment Variables

| Variable              | Default                                                   | Description            |
|-----------------------|-----------------------------------------------------------|------------------------|
| RABBITMQ_URL          | amqp://insighthub:insighthub_dev@rabbitmq:5672/           | RabbitMQ connection    |
| RABBITMQ_EXCHANGE     | insighthub                                                | Exchange name          |
| DATABASE_URL          | postgresql://insighthub:insighthub_dev@postgres:5432/insighthub | PostgreSQL connection  |
| QDRANT_URL            | http://qdrant:6333                                        | Qdrant endpoint        |
| QDRANT_COLLECTION_NAME| documents                                                 | Collection name        |
| WORKER_CONCURRENCY    | 2                                                         | Concurrent processing  |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main
```
