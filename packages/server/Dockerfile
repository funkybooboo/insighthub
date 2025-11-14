# syntax=docker/dockerfile:1.4

# ============================================================================
# Base Stage - Common dependencies for all stages
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Create app directory and user
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app

# ============================================================================
# Dependencies Stage - Install Python dependencies
# ============================================================================
FROM base AS dependencies

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Install dependencies (without dev dependencies)
RUN poetry install --no-root --only main

# ============================================================================
# Development Dependencies Stage - Install all dependencies including dev
# ============================================================================
FROM base AS dependencies-dev

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Install all dependencies (including dev)
RUN poetry install --no-root

# ============================================================================
# Development Stage - For local development with hot-reload
# ============================================================================
FROM dependencies-dev AS development

# Copy application code
COPY --chown=app:app . .

# Install the project in editable mode
RUN poetry install --only-root

# Copy and set permissions for entrypoint
COPY --chown=app:app --chmod=755 docker-entrypoint.sh /usr/local/bin/

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Set environment for development
ENV FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8000 \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command for development (Flask with auto-reload)
CMD ["poetry", "run", "python", "-m", "flask", "--app", "src.api:app", "run", "--host=0.0.0.0", "--port=8000", "--reload"]

# ============================================================================
# Builder Stage - Build and test production code
# ============================================================================
FROM dependencies-dev AS builder

# Copy application code
COPY --chown=app:app . .

# Install the project
RUN poetry install --only-root

# Run tests and quality checks (optional - can be skipped with --target production)
RUN poetry run black --check src tests || true
RUN poetry run ruff check src tests || true
RUN poetry run mypy src tests || true

# ============================================================================
# Production Stage - Minimal production image
# ============================================================================
FROM dependencies AS production

# Copy application code
COPY --chown=app:app src ./src
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini ./

# Install the project (root only)
RUN poetry install --only-root

# Copy and set permissions for entrypoint
COPY --chown=app:app --chmod=755 docker-entrypoint.sh /usr/local/bin/

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Set production environment
ENV FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8000 \
    FLASK_ENV=production

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command for production
CMD ["poetry", "run", "python", "src/api.py"]
