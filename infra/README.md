# Infrastructure

Shared infrastructure and configuration for InsightHub backend services.

## Structure

```
infra/
├── config/           # Environment configuration files
│   ├── .env.local.example    # Development template
│   ├── .env.prod.example     # Production template
│   ├── .env.test             # Test configuration
│   └── .gitignore            # Git ignore rules for env files
├── migrations/       # Database schema migrations
│   ├── *.sql                # Migration files
│   └── migrate.py           # Migration runner script
├── elk/              # ELK stack configuration
│   ├── filebeat/            # Filebeat config
│   └── logstash/            # Logstash config
└── Taskfile.yml      # Infrastructure management tasks
```

## Configuration

### Setup

1. **Copy development config:**
   ```bash
   cp infra/config/.env.local.example infra/config/.env.development
   ```

2. **Edit with your settings:**
   ```bash
   # infra/config/.env.development
   database_url=postgresql://your-db-url
   redis_url=redis://your-redis-url
   # ... etc
   ```

### Usage

Configuration is automatically loaded by both server and workers:

- **Server**: Loads via `shared.config` module
- **Workers**: Get config via Docker `env_file` directive
- **Single source of truth** for all backend services

## Database Migrations

### Run Migrations

```bash
# Run pending migrations
python infra/migrations/migrate.py

# Check migration status
python infra/migrations/migrate.py --status

# Create new migration
python infra/migrations/migrate.py --create "add_user_preferences"
```

### Migration Files

Located in `infra/migrations/` with format: `NNN_description.sql`

Example:
```sql
-- Migration: 005_add_user_preferences
-- Description: Add user preferences table
-- Created: 2024-01-15

CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ELK Stack

ELK (Elasticsearch, Logstash, Kibana) configuration for logging and monitoring.

### Components

- **Filebeat**: Log shipping from containers to Logstash
- **Logstash**: Log processing and filtering
- **Elasticsearch**: Log storage and search
- **Kibana**: Log visualization dashboard

### Usage

```bash
# Start ELK stack
docker compose -f docker-compose.elk.yml up -d

# View Kibana dashboard
open http://localhost:5601
```

## Tasks

Available infrastructure tasks:

```bash
# Show all tasks
task -d infra

# Run migrations
task -d infra migrate

# Check migration status
task -d infra migrate:status

# Validate configuration
task -d infra config:validate
```

## Development Workflow

1. **Setup config:** Copy and customize `.env.development`
2. **Run migrations:** Apply database schema changes
3. **Start services:** Use docker-compose files for local development
4. **Monitor logs:** Use ELK stack for log aggregation

## Production Deployment

- Use `.env.prod.example` as template for production
- Migrations run automatically during deployment
- ELK stack configured for production logging
- Configuration managed via deployment secrets