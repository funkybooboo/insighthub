# Database Migrations

This folder contains database migration scripts for the InsightHub server.

## Structure

```
migrations/
├── 001_initial_schema.sql    # Initial database schema
├── 002_add_workspaces.sql     # Workspace tables
├── 003_add_documents.sql      # Document tables
└── ...
```

## Running Migrations

Migrations can be run using your preferred database migration tool or manually:

```bash
psql -U username -d insighthub -f migrations/001_initial_schema.sql
```

## Current Schema

The application currently uses in-memory repositories for development.
When moving to production, implement SQL repositories and run these migrations.
