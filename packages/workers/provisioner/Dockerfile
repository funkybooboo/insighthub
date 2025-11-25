# Multi-stage Dockerfile for Provisioner Worker

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry && poetry config virtualenvs.create false

# ============================================================================
# Dependencies Stage
# ============================================================================
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-root

# ============================================================================
# Development Stage
# ============================================================================
FROM dependencies AS development

# Copy source code
COPY src/ ./src/

# Install in development mode
RUN poetry install --no-dev

# Default command for development
CMD ["python", "-m", "src.main"]

# ============================================================================
# Production Stage
# ============================================================================
FROM dependencies AS production

# Copy source code
COPY src/ ./src/

# Default command for production
CMD ["python", "-m", "src.main"]