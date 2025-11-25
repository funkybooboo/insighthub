# Docker Guide

Comprehensive Docker setup and deployment guide for InsightHub dual RAG system with ELK monitoring integration.

## Quick Start

### Production Deployment

```bash
# Build and start all production services
task build && task up

# Access points:
# Frontend: http://localhost:80 (Nginx)
# API: http://localhost:8000 (Flask production)
# ELK Monitoring: http://localhost:5601
```

### Development Environment

```bash
# Containerized development with hot reload
task build-dev && task up-dev

# Access points:
# Frontend Dev: http://localhost:3000 (Vite HMR)
# Backend Dev: http://localhost:5000 (Flask auto-reload)
# ELK Monitoring: http://localhost:5601
```

### Infrastructure Only

```bash
# Start core infrastructure services
task up-infra

# Services: PostgreSQL, Qdrant, MinIO, Ollama, RabbitMQ
# Use this for local development with services running in containers
```

## Architecture Overview

### Service Components

**Infrastructure Services** (always required):
- **PostgreSQL** (port 5432) - Primary database for users, workspaces, chat
- **Qdrant** (ports 6333, 6334) - Vector database for document embeddings
- **MinIO** (ports 9000, 9001) - Object storage for uploaded documents
- **Ollama** (port 11434) - Local LLM inference for embeddings and chat
- **RabbitMQ** (ports 5672, 15672) - Message queue for async processing

**Application Services**:
- **Server** (port 5000 dev / 8000 prod) - Flask backend with WebSocket support
- **Client** (port 3000 dev / 80 prod) - React frontend
- **Workers** - Background processing (parser, chucker, embedder, indexer, chat)

**Application Services**:
- **Server** (port 5000 dev, 8000 prod) - Flask backend
- **Client** (port 3000 dev, 80 prod) - React frontend

**Monitoring Stack**:
- **Elasticsearch** (port 9200) - Log storage and search
- **Logstash** (port 5044) - Log processing pipeline
- **Kibana** (port 5601) - Monitoring dashboard
- **Filebeat** - Log collection from containers

### Docker Compose Files

| File | Purpose | Services |
|------|---------|----------|
| `docker-compose.yml` | Core infrastructure | PostgreSQL, Qdrant, MinIO, Ollama, RabbitMQ |
| `docker-compose.dev.yml` | Development services | server-dev, client-dev |
| `docker-compose.prod.yml` | Production services | server-prod, client-prod |
| `docker-compose.workers.yml` | Background workers | All processing workers |
| `docker-compose.elk.yml` | ELK monitoring | Elasticsearch, Logstash, Kibana, Filebeat |

## Dockerfiles

### Server Dockerfile

**Multi-stage build** for optimization:

```dockerfile
FROM python:3.11-slim AS base
# Install system dependencies
FROM base AS dependencies
# Install Python dependencies
FROM base AS dependencies-dev
# Install development dependencies
FROM dependencies-dev AS development
# Development target with hot reload
FROM dependencies AS production
# Production target with optimizations
```

**Key Features**:
- **Non-root user**: Security best practice
- **Health checks**: `/health` endpoint monitoring
- **Optimized layers**: Minimal production image
- **Development support**: Hot reload with volume mounts

### Client Dockerfile

**Multi-stage build** for React application:

```dockerfile
FROM oven/bun:1.1.38-slim AS base
# Install dependencies
FROM base AS dependencies
# Build application
FROM dependencies AS builder
# Production target with Nginx
FROM nginx:1.27-alpine AS production
# Serve static files efficiently
```

**Key Features**:
- **Build optimization**: Separate build and runtime stages
- **Nginx serving**: Optimized static file serving
- **Compression**: Gzip compression enabled
- **Security headers**: Production-ready configuration

### Worker Dockerfiles

**Consistent structure** across all workers:

```dockerfile
FROM python:3.11-slim AS base
# Install dependencies
FROM base AS development
# Development with hot reload
FROM base AS production
# Optimized production image
```

## Configuration

### Environment Variables

**Development Configuration** (`.env`):
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key

# Database
DATABASE_URL=postgresql://insighthub:password@postgres:5432/insighthub

# Vector Database
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Message Queue
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

**Production Configuration**:
- Use environment variables or secrets management
- Enable all security headers
- Configure proper SSL certificates
- Set up monitoring and alerting

### Volume Management

**Persistent Data**:
```yaml
volumes:
  postgres_data:      # Database data
  qdrant_data:        # Vector database data
  minio_data:          # Object storage data
  ollama_data:         # LLM models cache
  rabbitmq_data:        # Message queue data
  elasticsearch_data:    # Log storage
```

**Development Volumes**:
```yaml
volumes:
  - ./packages/server/src:/app/src  # Hot reload
  - ./packages/client/src:/app/src   # Hot reload
```

## ELK Integration

### ELK Stack Architecture

```
Application Logs -> Filebeat -> Logstash -> Elasticsearch -> Kibana
```

**Components**:
- **Filebeat**: Collects logs from all containers
- **Logstash**: Processes and enriches log data
- **Elasticsearch**: Stores and indexes log data
- **Kibana**: Visualizes and searches logs

### Log Configuration

**Filebeat Configuration** (`elk/filebeat/filebeat.yml`):
```yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        match_fields: ["container"]
    - decode_json_fields:
          fields: ["message"]
          target: ""
```

**Logstash Configuration** (`elk/logstash/logstash.conf`):
```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [docker][container][name] {
    mutate {
      add_field => { "service_name" => "%{[docker][container][name]}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "insighthub-logs-%{+YYYY.MM.dd}"
  }
}
```

### Kibana Dashboards

**Access**: http://localhost:5601

**Pre-configured Dashboards**:
- **Application Logs**: Filter by service and log level
- **Error Tracking**: Monitor errors and exceptions
- **Performance Metrics**: Request latency and throughput
- **System Health**: Container resource usage

**Log Patterns**:
- **Structured JSON**: Consistent log format across services
- **Correlation IDs**: Track requests across services
- **Error Context**: Detailed error information
- **Performance Data**: Timing and resource usage

## Common Commands

### Service Management

```bash
# Start services
task up              # Production
task up-dev          # Development
task up-infra        # Infrastructure only
task up-elk          # ELK monitoring

# Stop services
task down            # Stop all
task restart         # Restart all

# View status
task ps              # Service status
task logs            # All logs
task logs-server     # Server logs only
task logs-client     # Client logs only
```

### Building Images

```bash
# Build all images
task build           # Production
task build-dev       # Development

# Build specific service
docker compose build server
docker compose build client
docker compose build ollama
```

### Development Workflow

```bash
# Start development environment
task build-dev && task up-dev

# View logs in real-time
task logs-server-dev
task logs-client-dev

# Restart services with code changes
task restart-dev

# Clean up
task down
task clean           # Remove containers and volumes
```

### Production Deployment

```bash
# Deploy production
task build && task up

# Enable monitoring
task up-elk

# Health checks
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:5601/api/status
```

## Health Checks

### Service Health Endpoints

```bash
# Backend health
curl http://localhost:5000/health

# Database connectivity
curl http://localhost:5000/health/database

# Vector database status
curl http://localhost:5000/health/qdrant

# Message queue status
curl http://localhost:5000/health/rabbitmq

# LLM service status
curl http://localhost:5000/health/ollama
```

### Docker Health Checks

**Built-in Health Checks**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Monitoring Health Status**:
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health check logs
docker inspect insighthub-server | jq '.[0].State.Health'
```

## Performance Optimization

### Image Optimization

**Multi-stage Builds**:
- Separate build and runtime environments
- Minimize production image size
- Exclude development dependencies

**Layer Caching**:
- Order operations from least to most frequently changing
- Use `.dockerignore` files effectively
- Leverage Docker build cache

### Resource Management

**Memory Limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

**CPU Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
    reservations:
      cpus: '0.5'
```

### Network Optimization

**Internal Networking**:
```yaml
networks:
  insighthub-network:
    driver: bridge
    internal: false
```

**Service Discovery**:
- Use service names for internal communication
- Configure proper DNS resolution
- Optimize connection pooling

## Security

### Container Security

**Non-root Users**:
```dockerfile
RUN addgroup --system app && adduser --system --group app
USER app
```

**Read-only Filesystem**:
```yaml
read_only: true
tmpfs:
  - /tmp
```

**Security Scanning**:
```bash
# Scan images for vulnerabilities
docker scan insighthub-server:latest
docker scan insighthub-client:latest
```

### Network Security

**Internal Networks**:
```yaml
networks:
  - insighthub-internal
  - insighthub-external
```

**Port Exposure**:
- Only expose necessary ports
- Use reverse proxy for production
- Configure firewall rules

### Secrets Management

**Environment Variables**:
```yaml
secrets:
  - db_password
  - jwt_secret
  - api_keys
```

**Production Secrets**:
- Use Docker secrets or external secret management
- Rotate secrets regularly
- Audit secret access

## Monitoring and Logging

### Application Logging

**Structured Logging**:
```python
# Python (Flask)
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'service': 'insighthub-server',
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', None)
        }
        return json.dumps(log_entry)
```

**Log Levels**:
- **DEBUG**: Detailed debugging information
- **INFO**: General information messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors

### Performance Monitoring

**Metrics Collection**:
- Request rate and latency
- Error rates by endpoint
- Database query performance
- Resource utilization

**Health Monitoring**:
- Service availability checks
- Resource usage monitoring
- Automated alerting
- Performance trend analysis

## Troubleshooting

### Common Issues

**Container Startup Problems**:
```bash
# Check container logs
docker compose logs server
docker compose logs client

# Check container status
docker compose ps

# Debug container startup
docker compose run --rm server bash
```

**Network Issues**:
```bash
# Check network connectivity
docker compose exec server ping postgres
docker compose exec server ping qdrant

# Check port exposure
docker compose port server
netstat -tulpn | grep :5000
```

**Volume Issues**:
```bash
# Check volume mounts
docker compose exec server ls -la /app/src

# Inspect volumes
docker volume inspect insighthub_postgres_data

# Clean up volumes
docker compose down -v
docker volume prune
```

**Performance Issues**:
```bash
# Monitor resource usage
docker stats

# Check memory usage
docker compose exec server free -h

# Profile application
docker compose exec server python -m cProfile -o profile.stats src/api.py
```

### Debug Mode

**Enable Debug Logging**:
```bash
# Set debug environment
export DEBUG=1
export LOG_LEVEL=DEBUG

# Restart services
task restart-dev
```

**Interactive Debugging**:
```bash
# Access container shell
docker compose exec server bash
docker compose exec client sh

# Run commands in container
docker compose run --rm server python -c "import sys; print(sys.version)"
```

## Best Practices

### Development Workflow

1. **Use Task Commands**: Prefer `task up-dev` over direct docker compose
2. **Volume Mounting**: Mount source directories for hot reload
3. **Environment Management**: Use `.env` files for configuration
4. **Regular Cleanup**: Use `task down` and `task clean` regularly
5. **Monitor Resources**: Use `docker stats` during development

### Production Deployment

1. **Build Optimization**: Use multi-stage builds for minimal images
2. **Security First**: Run as non-root, enable security scanning
3. **Health Monitoring**: Configure comprehensive health checks
4. **Log Aggregation**: Enable ELK stack for monitoring
5. **Resource Limits**: Set appropriate memory and CPU limits

### Maintenance

1. **Regular Updates**: Keep base images updated
2. **Security Scanning**: Regular vulnerability scanning
3. **Backup Strategy**: Regular data volume backups
4. **Performance Tuning**: Monitor and optimize resource usage
5. **Documentation**: Keep Docker documentation updated

## Additional Resources

### Documentation
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [ELK Stack Documentation](https://www.elastic.co/guide/)
- [Task Documentation](https://taskfile.dev/)

### Tools and Utilities
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Portainer](https://www.portainer.io/) - Web UI for Docker
- [cTop](https://github.com/bcicen/ctop) - Container monitoring
- [Lazydocker](https://github.com/jesseduffield/lazydocker) - Terminal UI

This comprehensive Docker setup ensures reliable deployment, monitoring, and maintenance of the InsightHub dual RAG system across development and production environments.