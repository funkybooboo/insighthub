# Document Router Worker

Document routing worker that orchestrates RAG pipeline selection and distribution.

## Responsibility

- Consume `document.chunked` events after text chunking
- Route documents to appropriate RAG pipelines (vector, graph, or both)
- Support configurable routing based on workspace settings
- Enable hybrid RAG by routing to multiple pipelines simultaneously

## Routing Logic

```
+-----------------+
| document.chunked |
+-----------------+
         |
         v
+-----------------+     +-----------------+
|   Router Logic  | --> |  Configuration  |
|                 |     |                 |
| * Workspace     |     | * Vector Only   |
| * Content Type  |     | * Graph Only    |
| * User Settings |     | * Hybrid        |
+-----------------+     +-----------------+
         |
    +----+----+
    |         |
    v         v
+---------+ +---------+
| Vector  | | Graph   |
| Pipeline| | Pipeline|
+---------+ +---------+
```

## Events

| Direction | Event              | Description                          |
|-----------|--------------------|--------------------------------------|
| Consumes  | document.chunked   | Triggered after document chunking    |
| Produces  | document.chunked   | Routes to vector.embedder queue      |
| Produces  | document.chunked   | Routes to graph.entity-extraction queue |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
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