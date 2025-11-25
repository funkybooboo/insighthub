# Graph Construction Worker

Graph RAG graph construction worker that builds Neo4j knowledge graphs from extracted entities and relationships.

## Responsibility

- Consume `document.communities_detected` events
- Retrieve entities and relationships from database
- Construct Neo4j graph with nodes and edges
- Publish `document.graph_constructed` events

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | document.communities_detected | Triggered when communities are detected |
| Produces  | document.graph_constructed  | Emitted after graph is constructed   |

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