# Docker Compose Setup Guide

Complete guide to running InsightHub with Docker Compose.

## Architecture Overview

InsightHub uses a multi-container architecture with the following services:

### Infrastructure (Base Services)
- **PostgreSQL** - Primary database
- **MinIO** - S3-compatible object storage
- **Ollama** - Local LLM service (llama3.2:1b + nomic-embed-text)
- **Qdrant** - Vector database for embeddings
- **Redis** - Cache and session store
- **RabbitMQ** - Message queue for worker communication

### Application Services
- **Server** (dev/prod) - Flask API server
- **Client** (dev/prod) - React frontend

### Worker Processes (Optional)
- **Ingestion Worker** - Document parsing and chunking
- **Embeddings Worker** - Vector generation and Qdrant indexing
- **Graph Worker** - Entity extraction and graph construction
- **Enrichment Worker** - External knowledge fetching
- **Query Worker** - Query context preparation
- **Retriever Worker** - Live internet data fetching
- **Notify Worker** - System notifications

---

## Quick Start

### Option 1: Infrastructure Only (For Local Development)

```bash
# Start all infrastructure services
task up-infra

# In separate terminals, run server and client locally
cd packages/server && poetry run python -m src.api
cd packages/client && bun run dev
```

**Services Started:**
- PostgreSQL: `localhost:5432`
- MinIO Console: `http://localhost:9001`
- Ollama API: `http://localhost:11434`
- Qdrant UI: `http://localhost:6334`
- Redis: `localhost:6379`
- RabbitMQ Management: `http://localhost:15672`

### Option 2: Development Mode (Containerized)

```bash
# Build and start development containers
task build-dev && task up-dev
```

**Access:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### Option 3: Production Mode

```bash
# Build and start production containers
task build && task up
```

**Access:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### Option 4: Full Stack (Infrastructure + Dev + Workers)

```bash
# TODO: Workers not yet implemented
task up-full
```

---

## Compose File Overview

### `docker-compose.yml` (Base Infrastructure)

Defines all infrastructure services:
- postgres
- minio
- ollama + ollama-setup
- qdrant
- redis
- rabbitmq

**Usage:**
```bash
docker compose -f docker-compose.yml up -d
```

### `docker-compose.dev.yml` (Development)

Extends base with development containers:
- server-dev (hot-reload enabled)
- client-dev (Vite dev server)

**Usage:**
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --profile dev
```

### `docker-compose.prod.yml` (Production)

Extends base with production containers:
- server-prod (optimized build)
- client-prod (Nginx static server)

**Usage:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --profile prod
```

### `docker-compose.workers.yml` (Worker Processes)

Defines all worker processes (TODO: Implementation pending):
- worker-ingestion
- worker-embeddings
- worker-graph
- worker-enrichment
- worker-query
- worker-retriever
- worker-notify

**Usage:**
```bash
docker compose -f docker-compose.yml -f docker-compose.workers.yml up -d --profile workers
```

---

## Common Tasks

### Start Services

```bash
# Infrastructure only
task up-infra

# Development
task up-dev

# Production
task up

# Workers (TODO)
task up-workers

# Everything
task up-full
```

### Stop Services

```bash
# Stop all
task down

# Stop specific service
docker compose stop server-dev
```

### View Logs

```bash
# All services
task logs

# Specific service
task logs-server-dev
task logs-client-dev
task logs-postgres
task logs-qdrant
task logs-rabbitmq
task logs-workers  # All workers
```

### Build Images

```bash
# Development images
task build-dev

# Production images
task build

# Specific service
task build-server
task build-client
```

### Restart Services

```bash
# Restart all
task restart-dev

# Restart specific service
docker compose restart server-dev
```

### Clean Up

```bash
# Remove containers and volumes
task clean

# Remove everything including images
docker compose down -v --rmi all
```

---

## Service Details

### PostgreSQL

**Port:** 5432  
**Credentials:**
- User: `insighthub`
- Password: `insighthub_dev`
- Database: `insighthub`

**Connection String:**
```
postgresql://insighthub:insighthub_dev@localhost:5432/insighthub
```

**Health Check:**
```bash
docker compose exec postgres pg_isready -U insighthub
```

### MinIO

**Ports:**
- API: 9000
- Console: 9001

**Credentials:**
- Access Key: `insighthub`
- Secret Key: `insighthub_dev_secret`

**Console:** `http://localhost:9001`

**Create Bucket:**
```bash
docker compose exec minio mc mb local/documents
```

### Ollama

**Port:** 11434  
**Models:**
- LLM: `llama3.2:1b`
- Embeddings: `nomic-embed-text`

**Test:**
```bash
curl http://localhost:11434/api/tags
```

**Models Auto-Pulled:** Yes (via ollama-setup service)

### Qdrant

**Ports:**
- API: 6333
- UI: 6334

**Web UI:** `http://localhost:6334`

**Create Collection:**
```bash
curl -X PUT http://localhost:6333/collections/documents \
  -H 'Content-Type: application/json' \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'
```

### Redis

**Port:** 6379  

**Test:**
```bash
docker compose exec redis redis-cli ping
# Expected: PONG
```

### RabbitMQ

**Ports:**
- AMQP: 5672
- Management UI: 15672

**Credentials:**
- User: `insighthub`
- Password: `insighthub_dev`

**Management UI:** `http://localhost:15672`

---

## Environment Variables

### Server Environment

```bash
# Python
PYTHONUNBUFFERED=1

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_ENV=development
FLASK_DEBUG=1

# Database
DATABASE_URL=postgresql://insighthub:insighthub_dev@postgres:5432/insighthub

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=insighthub
S3_SECRET_KEY=insighthub_dev_secret
S3_BUCKET_NAME=documents

# LLM
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Store
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=documents

# Cache
REDIS_URL=redis://redis:6379/0

# Message Queue
RABBITMQ_URL=amqp://insighthub:insighthub_dev@rabbitmq:5672/
```

### Client Environment

```bash
NODE_ENV=development
VITE_API_URL=http://localhost:5000
```

### Worker Environment

```bash
# Worker Config
WORKER_NAME=ingestion
WORKER_CONCURRENCY=4

# Plus all database, storage, and service URLs from server
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check service status
task ps

# View logs
task logs

# Restart specific service
docker compose restart <service-name>
```

### Port Conflicts

```bash
# Check what's using a port
lsof -i :5000
lsof -i :3000

# Change port in docker-compose files or stop conflicting service
```

### Database Issues

```bash
# Reset database
task down
docker volume rm insighthub_postgres_data
task up-dev
```

### Ollama Models Not Loaded

```bash
# Check ollama-setup logs
docker compose logs ollama-setup

# Manually pull models
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
```

### Qdrant Collection Missing

```bash
# Create collection manually
curl -X PUT http://localhost:6333/collections/documents \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }'
```

### Worker Connection Issues

```bash
# Check RabbitMQ is running
docker compose ps rabbitmq

# Check RabbitMQ management UI
open http://localhost:15672

# View worker logs
task logs-workers
```

### Clean Slate

```bash
# Nuclear option: remove everything
task clean
docker system prune -a --volumes
```

---

## Development Workflow

### 1. Infrastructure + Local Development

```bash
# Start infrastructure
task up-infra

# Terminal 1: Server
cd packages/server
poetry shell
python -m src.api

# Terminal 2: Client
cd packages/client
bun run dev
```

### 2. Full Containerized Development

```bash
# Build and start
task build-dev && task up-dev

# Code changes auto-reload via volumes
# Edit files in packages/server/src or packages/client/src

# View logs
task logs-server-dev
task logs-client-dev
```

### 3. Adding Workers (TODO)

```bash
# Start infrastructure + dev + workers
task up-full

# View worker logs
task logs-workers

# Restart specific worker
docker compose restart worker-ingestion
```

---

## Production Deployment

### Build Images

```bash
# Build production images
task build

# Or build specific service
task build-server
task build-client
```

### Deploy

```bash
# Start production stack
task up

# Or with workers
docker compose -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.workers.yml \
  up -d --profile prod --profile workers
```

### Health Checks

All services have health checks. Check status:

```bash
docker compose ps
```

Services with `healthy` status are ready.

---

## Network Architecture

All services run on the `insighthub_network` bridge network:

```
insighthub_network (172.x.x.x)
├── postgres        (postgres:5432)
├── minio           (minio:9000, minio:9001)
├── ollama          (ollama:11434)
├── qdrant          (qdrant:6333, qdrant:6334)
├── redis           (redis:6379)
├── rabbitmq        (rabbitmq:5672, rabbitmq:15672)
├── server-dev      (server-dev:8000)
├── client-dev      (client-dev:5173)
└── worker-*        (workers connect to services)
```

Services communicate using internal hostnames (e.g., `postgres:5432`).

---

## Volume Management

### Named Volumes

```bash
insighthub_postgres_data   # PostgreSQL data
insighthub_minio_data      # MinIO objects
insighthub_ollama_data     # Ollama models
insighthub_qdrant_data     # Qdrant vectors
insighthub_redis_data      # Redis cache
insighthub_rabbitmq_data   # RabbitMQ queues
```

### Backup Volumes

```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U insighthub insighthub > backup.sql

# Backup MinIO
docker compose exec minio mc mirror local/documents ./minio-backup

# Backup Qdrant
curl http://localhost:6333/collections/documents/snapshots > qdrant-snapshot.json
```

### Restore Volumes

```bash
# Restore PostgreSQL
cat backup.sql | docker compose exec -T postgres psql -U insighthub insighthub
```

---

## Next Steps

1. ✅ Infrastructure services configured
2. ✅ Server and client containers working
3. ✅ Qdrant added to stack
4. ✅ Redis and RabbitMQ configured
5. TODO: Implement worker Dockerfiles
6. TODO: Test full stack with workers
7. TODO: Production deployment guide
8. TODO: Kubernetes manifests

---

*Last Updated: 2025-11-18*
