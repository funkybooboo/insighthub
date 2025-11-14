# Docker Guide

InsightHub uses Docker Compose with profiles for production and development environments.

## Quick Start

```bash
# Production
task build && task up

# Development (containerized with hot-reload)
task build-dev && task up-dev

# Development (local + infrastructure only)
task up-infra
```

## Architecture

**Infrastructure** (shared): `postgres`, `minio`, `ollama`
**Production** (profile: prod): `server-prod`, `client-prod`
**Development** (profile: dev): `server-dev`, `client-dev`

Key features:
- Multi-stage builds for optimal image size
- Non-root users for security
- Health checks on all services
- Hot-reload in development mode
- Entrypoint scripts handle migrations

## Common Commands

```bash
# Services
task up              # Start production
task up-dev          # Start development
task up-infra        # Infrastructure only
task down            # Stop all
task ps              # Service status

# Building
task build           # Build production images
task build-dev       # Build development images

# Logs
task logs-server-dev # Development server logs
task logs-client-dev # Development client logs
task logs-postgres   # Database logs

# Quality
task check           # Run all checks

# Cleanup
task clean           # Remove all containers/volumes
```

## Development Workflow

### Option 1: Containerized (Recommended)
```bash
task build-dev && task up-dev
# Edit code, changes auto-reload
task check  # Before committing
task down
```

### Option 2: Local Development
```bash
task up-infra  # Start infrastructure

# Terminal 1
cd packages/server && poetry install && task server

# Terminal 2
cd packages/client && bun install && task dev
```

## Dockerfiles

### Server (Python)
Stages: `base` -> `dependencies` -> `development` / `production`
- Development: Flask with auto-reload
- Production: Minimal image, no dev dependencies
- Non-root user: `app`
- Port: 8000

### Client (TypeScript/Bun)
Stages: `base` -> `dependencies` -> `development` / `builder` -> `production`
- Development: Vite dev server (port 5173)
- Production: Nginx serving static files (port 80)
- Non-root users: `app` (build), `nginx` (serve)

## Entrypoint Scripts

**Server**: Waits for PostgreSQL, runs migrations, initializes database, starts Flask
**Client**: Injects runtime config, configures nginx, starts web server

Both use color-coded logging and handle errors gracefully.

## Troubleshooting

```bash
# Services won't start
task ps && task logs

# Database issues
task down && docker volume rm insighthub_postgres_data && task up-dev

# Port conflicts
lsof -i :5000 && lsof -i :3000

# Hot-reload not working
task restart-dev

# Clear build cache
docker builder prune && task build-dev

# Memory issues (Ollama)
docker stats  # Check usage, increase Docker memory limit if needed
```

## Best Practices

1. Use Task commands, not docker compose directly
2. Run `task check` before commits
3. Use `--profile` explicitly in docker compose commands
4. Clean up regularly with `task down`
5. Monitor resources with `docker stats`

## CI/CD

```yaml
# GitHub Actions example
- name: Install Task
  uses: arduino/setup-task@v2

- name: Run checks
  run: task check

- name: Build production
  run: task build
```

## Additional Resources

- [Task Commands](./taskfile-setup.md)
- [Architecture](./architecture.md)
- [Docker Compose Docs](https://docs.docker.com/compose/)
