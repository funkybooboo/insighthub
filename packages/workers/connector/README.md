# Connector Worker

Graph RAG connector worker - builds graph nodes and edges in Neo4j.

## Responsibility

- Consume embedding.created events
- Extract entities and relationships from document chunks
- Create nodes and edges in Neo4j graph database
- Publish graph.updated events

## Events

| Direction | Event              | Description                          |
|-----------|--------------------|--------------------------------------|
| Consumes  | embedding.created  | Triggered when embeddings are ready  |
| Produces  | graph.updated      | Emitted after graph is updated       |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| NEO4J_URL          | bolt://neo4j:7687                                 | Neo4j connection       |
| WORKER_CONCURRENCY | 2                                                 | Concurrent processing  |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main
```
