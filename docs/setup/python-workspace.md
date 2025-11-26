# Python Workspace Setup

This project uses a Python workspace structure similar to the TypeScript/Bun workspace setup. All Python packages now properly declare their dependencies on the shared library.

## Structure

```
insighthub/
+-- packages/
    +-- shared/python/        # Shared library (shared-python)
    +-- server/               # API server (depends on shared)
    +-- workers/              # Worker packages (all depend on shared)
        +-- general/
        |   +-- chat/
        |   +-- chunker/
        |   +-- enricher/
        |   +-- infrastructure-manager/
        |   +-- parser/
        |   +-- router/
        |   +-- wikipedia/
        +-- vector/
        |   +-- processor/
        |   +-- query/
        +-- graph/
            +-- connector/
            +-- construction/
            +-- preprocessor/
            +-- query/
```

## How It Works

All packages (server and workers) now use **path dependencies** with `develop = true`:

```toml
[tool.poetry.dependencies]
python = "^3.11"
shared-python = {path = "../shared/python", develop = true}
```

This means:
- No need to rebuild and reinstall the shared package after changes
- Changes to shared code are immediately available to all consumers
- No duplicate dependencies - everything is defined once in the shared package
- Clean mypy imports - `shared.*` is no longer in `ignore_missing_imports`

## Installation

### Automated Installation (Recommended)

Run the installation script from the project root:

```bash
./install-python-workspace.sh
```

This will:
1. Install and build the shared package
2. Install the server with the shared dependency
3. Install all workers with the shared dependency

### Manual Installation

If you prefer to install packages individually:

```bash
# 1. Install shared package first
cd packages/shared/python
poetry lock
poetry install --no-root
poetry build
cd ../../..

# 2. Install server
cd packages/server
poetry lock
poetry install --no-root
cd ../..

# 3. Install a specific worker
cd packages/workers/vector/processor
poetry lock
poetry install --no-root
cd ../../../..
```

## Benefits

### Before (Duplicated Dependencies)

**Server pyproject.toml:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0.0"
pika = "^1.3.0"
psycopg2-binary = "^2.9.0"
qdrant-client = "^1.7.0"
# ... 20+ more dependencies
```

**Worker pyproject.toml:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
pika = "^1.3.2"        # Duplicate!
psycopg2-binary = "^2.9.0"  # Duplicate!
qdrant-client = "^1.7.0"    # Duplicate!
```

### After (Workspace Dependencies)

**Server pyproject.toml:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
shared-python = {path = "../shared/python", develop = true}
# Only server-specific dependencies (flask, etc.)
```

**Worker pyproject.toml:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
shared-python = {path = "../../../shared/python", develop = true}
# Only worker-specific dependencies (if any)
```

## Development Workflow

### Local Development (without Docker)

1. **Make changes to shared code:**
   ```bash
   # Edit files in packages/shared/python/src/shared/
   vim packages/shared/python/src/shared/worker/worker.py
   ```

2. **Changes are immediately available:**
   ```bash
   # No rebuild needed! Just run your code
   cd packages/server
   poetry run python -m src.api
   ```

   The path dependency with `develop = true` means changes to shared code are immediately available.

### Docker Builds

For Docker builds, the Dockerfiles copy the entire shared package source:

```bash
# Build Docker images (automatically builds shared package first)
task build

# Or manually:
cd packages/shared/python
poetry build
task build
```

The Dockerfiles copy `packages/shared/python/` into the container at the correct relative path, allowing Poetry to resolve the path dependency during the Docker build.

## Troubleshooting

### Lock file out of date

If you see "poetry.lock is out of date", run:
```bash
poetry lock
```

### Shared package not found

Make sure you've built the shared package:
```bash
cd packages/shared/python
poetry build
```

### Import errors

Ensure you've installed dependencies:
```bash
poetry install --no-root
```

## Comparison with TypeScript Workspace

**TypeScript (Bun workspaces):**
```json
{
  "workspaces": ["packages/client", "packages/cli", "packages/shared/typescript"],
  "dependencies": {
    "@insighthub/shared-typescript": "workspace:*"
  }
}
```

**Python (Poetry path dependencies):**
```toml
[tool.poetry.dependencies]
shared-python = {path = "../shared/python", develop = true}
```

Both achieve the same goal: centralized dependency management with editable installations.
