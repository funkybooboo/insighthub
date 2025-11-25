# Chucker Worker

Document chunker worker - splits parsed documents into smaller chunks for embedding.

## Responsibility

- Consume document.parsed events
- Split documents into chunks using configurable strategies
- Store chunks in PostgreSQL
- Publish document.chunked events

## Events

| Direction | Event            | Description                         |
|-----------|------------------|-------------------------------------|
| Consumes  | document.parsed  | Triggered when document is parsed   |
| Produces  | document.chunked | Emitted after chunking is complete  |

## Environment Variables

| Variable           | Default                                                   | Description            |
|--------------------|-----------------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/           | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                                | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:insighthub_dev@postgres:5432/insighthub | PostgreSQL connection  |
| WORKER_CONCURRENCY | 4                                                         | Concurrent processing  |
| CHUNK_SIZE         | 1000                                                      | Characters per chunk   |
| CHUNK_OVERLAP      | 200                                                       | Overlap between chunks |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main
```
