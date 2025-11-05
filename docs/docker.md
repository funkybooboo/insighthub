# Docker + Make Integration Guide

This project integrates Make commands with Docker for consistent development and deployment workflows.

## Quick Start

From the project root, you can use the root-level Makefile to orchestrate all services:

```bash
# Show all available commands
make help

# Start development services (hot reload enabled)
make dev

# Run quality checks on all packages
make check

# Start production services
make up
```

## Architecture

Both the server and client Dockerfiles use **multi-stage builds** with the following stages:

### Server (Python) Stages

1. **base** - Base Python image with Poetry and Make
2. **development** - All dependencies including dev tools
3. **quality** - Runs `make check` (format, lint, type-check, test)
4. **production** - Production-only dependencies

### Client (TypeScript/Bun) Stages

1. **base** - Bun runtime with Make and dependencies
2. **development** - All source files for development
3. **quality** - Runs `make check` (format-check, lint, build)
4. **builder** - Builds production assets
5. **production** - Nginx serving static files

## Root-Level Commands

```bash
# Development
make dev              # Start both client and server in dev mode
make dev-server       # Start only server (with hot reload)
make dev-client       # Start only client (with hot reload)

# Quality Checks
make check            # Run checks on both packages
make check-server     # Check server code (format, lint, type-check, test)
make check-client     # Check client code (format-check, lint, build)

# Production
make up               # Start production services
make down             # Stop all services

# Building
make build            # Build both production images
make build-server     # Build server image only
make build-client     # Build client image only

# Utilities
make logs             # Show logs from all services
make logs-server      # Show server logs only
make logs-client      # Show client logs only
make clean            # Remove all containers, images, volumes
```

## Docker Compose Profiles

The `docker-compose.yml` uses profiles to organize services:

### Default Profile (Production)
```bash
docker compose up
```
Starts:
- `server` - Production Python server
- `client` - Production React app (nginx)

### Development Profile
```bash
docker compose --profile dev up
```
Starts:
- `server-dev` - Development server with hot reload (uses `make run`)
- `client-dev` - Development client with Vite HMR (uses `make dev`)

Both mount source code as volumes for instant feedback.

### Quality Check Profile
```bash
docker compose --profile check build server-check client-check
```
Builds the `quality` stage which runs:
- **Server**: `make check` - format, lint, type-check, test
- **Client**: `make check` - format-check, lint, build

This is perfect for CI/CD pipelines!

## Package-Level Commands

Each package has its own Makefile that Docker uses:

### Server (`packages/server/Makefile`)

```bash
cd packages/server

make install      # Install dependencies
make test         # Run tests with coverage
make format       # Format code (black, isort, ruff --fix)
make lint         # Run ruff linter
make type-check   # Run mypy type checker
make check        # Run all checks (format, lint, type-check, test)
make clean        # Clean generated files
make run          # Run the application
```

### Client (`packages/client/Makefile`)

```bash
cd packages/client

make install      # Install dependencies
make dev          # Run dev server
make build        # Build for production
make lint         # Run ESLint
make format       # Format with Prettier
make format-check # Check formatting
make test         # Run tests
make check        # Run all checks (format-check, lint, build)
make clean        # Clean generated files
make preview      # Preview production build
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run server quality checks
        run: make check-server

      - name: Run client quality checks
        run: make check-client
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
make check-server && make check-client
```

## Benefits

1. **Consistency**: Same commands work locally and in Docker
2. **Simplicity**: One command (`make check`) runs all quality checks
3. **CI/CD Ready**: Quality stage perfect for automated testing
4. **Documentation**: `make help` shows all available commands
5. **Maintainability**: Update commands in one place (Makefile)

## Development Workflow

```bash
# 1. Start development services
make dev

# 2. Code in your editor (changes hot-reload automatically)
# Server: http://localhost:8000
# Client: http://localhost:5173

# 3. Run checks before committing
make check

# 4. Build and test production images
make build
make up

# 5. Clean up
make down
```

## Troubleshooting

### Quality checks fail during build
If `make check` fails in the Docker quality stage, you can:
1. Run checks locally: `cd packages/server && make check`
2. Fix issues: `make format` (auto-fixes most issues)
3. Rebuild: `make build`

### Development server not hot-reloading
Ensure volumes are mounted correctly in `docker-compose.yml`:
```yaml
volumes:
  - ./packages/server:/app  # Server
  - ./packages/client:/app  # Client
```

### Port conflicts
Change ports in `docker-compose.yml` if 8000, 3000, or 5173 are taken.

## Advanced Usage

### Build specific stage
```bash
# Build only the quality stage
docker build --target quality -t insighthub-server:quality packages/server/

# Run quality checks
docker run insighthub-server:quality
```

### Override make target
```bash
# Run tests only
docker compose run server-dev make test

# Format code
docker compose run server-dev make format
```

### Multi-architecture builds
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t insighthub-server packages/server/
```
