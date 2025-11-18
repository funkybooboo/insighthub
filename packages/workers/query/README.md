# Query Preprocessing Worker

## Overview
The Query Worker prepares context for user queries so that the API server can be fast and responsive.

## Responsibilities
- Retrieve vector neighbors
- Expand graph neighborhood
- Perform query classification (vector / graph / hybrid)
- Pre-compute RAG inputs
- Cache query context for the server to stream

## Consumes Events
- `query.prepare`

## Produces Events
- `query.ready`

## Architecture
User → API → Query Worker → cached context → server streams response

## Running Locally

task dev
poetry run python src/main.py


## Environment Variables

QDRANT_URL=
DATABASE_URL=
OLLAMA_BASE_URL=
RABBITMQ_URL=


## Testing

pytest


## Extending
Add new routing algorithms or hybrid RAG logic.
