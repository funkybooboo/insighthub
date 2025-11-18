# Retriever Worker

## Overview
Fetches live information from the internet (authors, institutions, datasets, related papers).

## Responsibilities
- Hit remote APIs (arXiv, Semantic Scholar, OpenAlex)
- Cache API responses
- Publish new related documents into ingestion pipeline

## Consumes Events
- `retrieval.requested`

## Produces Events
- `retrieval.complete`
- Optional: `document.uploaded`

## Running Locally

task dev
poetry run python src/main.py


## Environment Variables

OPENALEX_API_KEY=
RABBITMQ_URL=


## Testing

pytest


## Extending
Add new API integrations or caching layers.
