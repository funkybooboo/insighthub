# Multi-stage Dockerfile for Retriever Worker

FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.7.1

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Development stage
FROM base as development

# Install all dependencies including dev
RUN poetry install --no-root

# Copy source code
COPY src ./src

# Run worker
CMD ["poetry", "run", "python", "-m", "src.main"]

# Production stage
FROM base as production

# Install only production dependencies
RUN poetry install --only main --no-root

# Copy source code
COPY src ./src

# Run worker with optimizations
CMD ["poetry", "run", "python", "-O", "-m", "src.main"]
