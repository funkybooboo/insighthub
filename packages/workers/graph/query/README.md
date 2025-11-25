# Graph Query Worker

Graph RAG graph query worker that handles graph-based retrieval and traversal queries.

## Responsibility

- Consume `chat.graph_query` events
- Perform graph traversal and retrieval operations
- Return relevant context for LLM generation
- Publish `chat.graph_query_completed` or `chat.graph_query_failed` events

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | chat.graph_query           | Triggered for graph-based queries    |
| Produces  | chat.graph_query_completed | Emitted with query results           |
| Produces  | chat.graph_query_failed    | Emitted on query errors              |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
| NEO4J_URL          | bolt://neo4j:7687                                 | Neo4j connection       |
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