# Database Migrations

This directory contains raw PostgreSQL migration files for InsightHub.

## Running Migrations

### Apply migrations (up)

From the project root, run:

```bash
psql -U insighthub -d insighthub -f migrations/001_initial_schema.sql
```

Or if using Docker:

```bash
docker compose exec postgres psql -U insighthub -d insighthub -f /migrations/001_initial_schema.sql
```

### Rollback migrations (down)

From the project root, run:

```bash
psql -U insighthub -d insighthub -f migrations/down/001_initial_schema.sql
```

Or if using Docker:

```bash
docker compose exec postgres psql -U insighthub -d insighthub -f /migrations/down/001_initial_schema.sql
```

## Migration Files

- `001_initial_schema.sql` - Initial database schema with all tables
  - workspaces
  - vector_rag_configs
  - graph_rag_configs
  - documents
  - chat_sessions
  - chat_messages
  - default_rag_configs

## Notes

- All tables include `created_at` and `updated_at` timestamps
- `updated_at` columns are automatically updated via PostgreSQL triggers
- Foreign keys use `ON DELETE CASCADE` for cleanup
- The pgvector extension is enabled for vector storage support
