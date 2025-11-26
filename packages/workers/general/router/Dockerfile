# Multi-stage Dockerfile for Router Worker

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.8.1

# Configure poetry - install globally, not in virtualenv
RUN poetry config virtualenvs.create false

# Copy shared package source at the correct relative path
# Path dependency in pyproject.toml: {path = "../../../shared/python"}
COPY packages/shared/python/ ../../../shared/python/

# Copy dependency files
COPY packages/workers/general/router/pyproject.toml packages/workers/general/router/poetry.lock* ./

# Development stage
FROM base AS development

# Install all dependencies including dev
RUN poetry install --no-root

# Copy source code
COPY packages/workers/general/router/src ./src

# Run worker
CMD ["poetry", "run", "python", "-m", "src.main"]

# Production stage
FROM base AS production

# Install only production dependencies
RUN poetry install --only main --no-root

# Copy source code
COPY packages/workers/general/router/src ./src

# Run worker with optimizations
CMD ["poetry", "run", "python", "-O", "-m", "src.main"]