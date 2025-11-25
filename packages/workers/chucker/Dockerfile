# Multi-stage Dockerfile for Chucker Worker

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.8.1

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy shared package wheel (latest version)
COPY packages/shared/python/dist/insighthub_shared-0.1.1-py3-none-any.whl /tmp/

# Install shared package
RUN pip install /tmp/insighthub_shared-0.1.1-py3-none-any.whl

# Copy dependency files
COPY packages/workers/chucker/pyproject.toml packages/workers/chucker/poetry.lock* ./

# Development stage
FROM base AS development

# Install all dependencies including dev
RUN poetry install --no-root

# Copy source code
COPY packages/workers/chucker/src ./src

# Run worker
CMD ["poetry", "run", "python", "-m", "src.main"]

# Production stage
FROM base AS production

# Install only production dependencies
RUN poetry install --only main --no-root

# Copy source code
COPY packages/workers/chucker/src ./src

# Run worker with optimizations
CMD ["poetry", "run", "python", "-O", "-m", "src.main"]
