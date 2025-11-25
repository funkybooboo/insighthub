# Environment Configuration

This directory contains environment configuration files and utilities for InsightHub.

## Environment Files

- `.env.local.example` - Example local development configuration
- `.env.prod.example` - Example production configuration
- `.env.local` - Your local development environment (ignored by git)
- `.env.test` - Test environment configuration (ignored by git)

## Setup

1. Copy the appropriate example file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Edit `.env.local` with your specific configuration values.

## Usage

### Source Environment Variables

Use the `source.sh` script to load environment variables into your shell:

```bash
# Source local development environment
./source.sh .env.local

# Source production environment
./source.sh .env.prod

# Source default (tries .env.local first, then .env)
./source.sh
```

### For Persistent Environment Variables

Add to your shell profile (e.g., `~/.bashrc` or `~/.zshrc`):

```bash
source /path/to/insighthub/infra/config/source.sh
```

## Configuration

The shared configuration system (`packages/shared/python/src/shared/config.py`) now relies on environment variables being set externally. It no longer automatically loads .env files.

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OLLAMA_BASE_URL` - Ollama API endpoint
- `QDRANT_HOST`, `QDRANT_PORT` - Qdrant vector database
- `SECRET_KEY`, `JWT_SECRET_KEY` - Security keys
- And many more (see `.env.local.example` for complete list)

## Security

- Never commit actual `.env` files to version control
- Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
- Keep API keys and database credentials secure