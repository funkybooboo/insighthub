# syntax=docker/dockerfile:1.4

# ============================================================================
# Base Stage - Common dependencies for all stages
# ============================================================================
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user and group
RUN groupadd -r app && useradd -r -g app -m app
WORKDIR /app
RUN chown -R app:app /app

# ============================================================================
# Dependencies Stage - Install Python dependencies
# ============================================================================
FROM base AS dependencies

# Install Poetry
USER root
RUN pip install poetry

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Install all dependencies (including ML dependencies)
USER app
RUN poetry install --only=main

# ============================================================================
# Development Stage - For local development with hot-reload
# ============================================================================
FROM dependencies AS development

# Copy application code
COPY --chown=app:app src/ ./src/
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app pyproject.toml poetry.lock README.md ./

# Copy and set permissions for entrypoint script
COPY --chown=app:app --chmod=755 docker-entrypoint.sh /usr/local/bin/

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables for development
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command for development
CMD ["python", "--version"]

# ============================================================================
# Production Stage - Final runtime image
# ============================================================================
FROM base AS production

# Copy installed dependencies from dependencies stage
COPY --from=dependencies --chown=app:app /home/app/.cache/pypoetry /home/app/.cache/pypoetry
COPY --from=dependencies --chown=app:app /home/app/.local /home/app/.local

# Copy application code
COPY --chown=app:app src/ ./src/
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app pyproject.toml poetry.lock README.md ./

# Copy and set permissions for entrypoint script
COPY --chown=app:app --chmod=755 docker-entrypoint.sh /usr/local/bin/

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/home/app/.local/bin:$PATH"

# Run the actual Flask application
CMD ["python", "-m", "src.api"]
