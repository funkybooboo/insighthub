# Infrastructure Manager Worker

Consolidated infrastructure management worker for workspace provisioning and deletion.

## Responsibility

- Consume `workspace.provision_requested` and `workspace.deletion_requested` events
- Provision infrastructure for new workspaces (Qdrant collections, Neo4j schemas, MinIO buckets)
- Clean up infrastructure when workspaces are deleted
- Publish `workspace.provision_status` and `workspace.deletion_status` events

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | workspace.provision_requested | Triggered when workspace is created |
| Consumes  | workspace.deletion_requested | Triggered when workspace is deleted |
| Produces  | workspace.provision_status | Emitted with provisioning results    |
| Produces  | workspace.deletion_status  | Emitted with deletion results        |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
| QDRANT_URL         | http://qdrant:6333                                | Qdrant vector database |
| NEO4J_URL          | bolt://neo4j:7687                                 | Neo4j graph database   |
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