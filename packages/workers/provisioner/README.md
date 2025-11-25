# InsightHub Provisioner Worker

Workspace provisioner worker that creates RAG infrastructure for workspaces.

## Overview

This worker consumes `workspace.provision_requested` events and provisions the necessary infrastructure:

- Qdrant vector collections for vector RAG
- PostgreSQL workspace metadata updates
- Future: Neo4j graph databases for graph RAG

## Development

```bash
poetry install
poetry run pytest tests/
```