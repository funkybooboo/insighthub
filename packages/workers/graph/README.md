# Graph Builder Worker

## Overview
Builds the knowledge graph representation for documents using entity and relationship extraction.

## Responsibilities
- Extract entities using LLM or spaCy
- Extract relationships between entities
- Build graph nodes + edges
- Store graph in Postgres or Neo4j
- Publish a completion event

## Consumes Events

- `document.graph.build`

## Produces Events

- `graph.build.complete`

## Architecture

Document chunks → entity extraction → link extraction → graph storage.

## Running Locally

task dev
poetry run python src/main.py


## Environment Variables

DATABASE_URL=
RABBITMQ_URL=
OLLAMA_BASE_URL=

## Testing

pytest

## Extending

Add new graph algorithms or knowledge linkers.
