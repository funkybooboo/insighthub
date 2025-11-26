# Docker and Workspace Updates

This document summarizes the updates made to support Python workspace-style dependencies in Docker builds.

## Changes Made

### 1. Python Package Dependencies

**All Python packages now use path dependencies:**

```toml
# Before (duplicated dependencies)
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0.0"
pika = "^1.3.0"
psycopg2-binary = "^2.9.0"
# ... many more

# After (workspace dependency)
[tool.poetry.dependencies]
python = "^3.11"
shared-python = {path = "../shared/python", develop = true}
# Only package-specific deps
```

**Packages Updated:**
- ✅ `packages/server/pyproject.toml`
- ✅ All worker `pyproject.toml` files (15 workers total)

### 2. Dockerfile Changes

**Before (wheel-based approach):**
```dockerfile
# Copy and install wheel
COPY packages/shared/python/dist/shared_python-0.1.1-py3-none-any.whl /tmp/
RUN pip install /tmp/shared_python-0.1.1-py3-none-any.whl

# Copy dependency files
COPY packages/server/pyproject.toml packages/server/poetry.lock ./

# Install dependencies
RUN poetry install --no-root
```

**After (path dependency approach):**
```dockerfile
# Copy shared package source at correct relative path
COPY packages/shared/python/ ../shared/python/

# Copy dependency files
COPY packages/server/pyproject.toml packages/server/poetry.lock ./

# Install dependencies - Poetry resolves path dependency
RUN poetry install --no-root
```

**Dockerfiles Updated:**
- ✅ `packages/server/Dockerfile`
- ✅ `packages/workers/vector/processor/Dockerfile`
- ✅ `packages/workers/vector/query/Dockerfile`
- ✅ `packages/workers/general/parser/Dockerfile`
- ✅ `packages/workers/general/chat/Dockerfile`
- ✅ `packages/workers/general/chunker/Dockerfile`
- ✅ `packages/workers/general/enricher/Dockerfile`
- ✅ `packages/workers/general/infrastructure-manager/Dockerfile`
- ✅ `packages/workers/general/router/Dockerfile`
- ✅ `packages/workers/general/wikipedia/Dockerfile`
- ✅ `packages/workers/graph/connector/Dockerfile`
- ✅ `packages/workers/graph/construction/Dockerfile`
- ✅ `packages/workers/graph/preprocessor/Dockerfile`
- ✅ `packages/workers/graph/query/Dockerfile`

### 3. Docker Compose Files

**Status:** ✅ No changes needed

The docker-compose files already correctly:
- Set build context to project root (`.`)
- Reference Dockerfiles with correct paths
- Pass environment variables properly

### 4. Taskfile.yml

**Status:** ✅ Working correctly

The build process:
```bash
task build
```

1. Calls `task shared:build` (defined in `packages/shared/python/Taskfile.yml`)
2. Runs `poetry build` to create wheel (needed for reference, not for Docker)
3. Runs `docker compose build` which copies shared source into containers

### 5. Installation Scripts

**New Files Created:**
- ✅ `install-python-workspace.sh` - Automated local installation
- ✅ `PYTHON_WORKSPACE.md` - Complete documentation
- ✅ `DOCKER_WORKSPACE_UPDATE.md` - This file

## How It Works

### Local Development

1. Install with path dependencies:
   ```bash
   ./install-python-workspace.sh
   ```

2. Changes to shared code are immediately available (no rebuild needed)
   ```bash
   # Edit shared code
   vim packages/shared/python/src/shared/worker/worker.py

   # Run immediately - changes are live
   cd packages/server
   poetry run python -m src.api
   ```

### Docker Builds

1. Shared package source is copied into containers at the correct relative path
2. Poetry resolves the path dependency during `poetry install`
3. No version hardcoding - always uses latest shared code

```bash
# Build everything
task build

# Build specific service
task build-server
```

## Benefits

1. **No Duplicate Dependencies:** All common dependencies defined once in shared package
2. **Editable Installs:** Local changes immediately available without rebuild
3. **Version Consistency:** No version mismatches between packages
4. **Clean Type Checking:** Proper imports from shared package
5. **Docker Compatibility:** Works in both local and container environments

## Testing

### Test Local Setup
```bash
# Install packages
./install-python-workspace.sh

# Verify imports work
cd packages/server
poetry run python -c "from shared.worker import Worker; print('Success!')"
```

### Test Docker Build
```bash
# Build all images
task build

# Check build succeeded
docker images | grep insighthub
```

### Test Docker Run
```bash
# Start infrastructure
task up-infra

# Start production stack
task up

# Check logs
task logs-server
```

## Troubleshooting

### Poetry lock file out of date

**Issue:** `pyproject.toml changed significantly since poetry.lock was last generated`

**Solution:**
```bash
cd packages/server  # or worker directory
poetry lock
poetry install
```

### Docker build fails to find shared package

**Issue:** `Path ../shared/python does not exist`

**Solution:** Ensure you're building from project root with correct context:
```bash
# Build from root
task build

# Or with docker compose directly
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
```

### Import errors in Docker container

**Issue:** `ModuleNotFoundError: No module named 'shared'`

**Solution:** Verify the COPY command in Dockerfile has correct relative path:
- For server: `../shared/python`
- For general workers: `../../../../shared/python`
- For vector/graph workers: `../../../shared/python`

## Migration Notes

**Breaking Changes:**
- All `pyproject.toml` files now use path dependencies
- Dockerfiles now copy shared source instead of wheel
- `poetry lock` must be run for each package

**Non-Breaking:**
- Docker compose files unchanged
- Taskfile.yml build process unchanged
- Environment variables unchanged

## Next Steps

1. ✅ Python workspace structure implemented
2. ✅ All Dockerfiles updated
3. ✅ Documentation created
4. ⏳ Test Docker build completion
5. ⏳ Run integration tests

## Comparison with TypeScript

**TypeScript (Bun Workspaces):**
```json
{
  "workspaces": ["packages/client", "packages/cli", "packages/shared/typescript"],
  "dependencies": {
    "@insighthub/shared-typescript": "workspace:*"
  }
}
```

**Python (Poetry Path Dependencies):**
```toml
[tool.poetry.dependencies]
shared-python = {path = "../shared/python", develop = true}
```

Both achieve centralized dependency management with editable installations.
