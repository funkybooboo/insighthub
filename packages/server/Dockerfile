# syntax=docker/dockerfile:1.4

# ============================================================================
# Base Stage - Common dependencies for all stages
# ============================================================================
FROM python:3.11-slim AS base

# Create app user and group
RUN groupadd -r app && useradd -r -g app -m app
WORKDIR /app
RUN chown -R app:app /app

# ============================================================================
# Dependencies Stage - Install Python dependencies
# ============================================================================
FROM base AS dependencies

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Install main dependencies using pip
USER app
RUN pip install --user flask flask-cors flask-socketio sqlalchemy psycopg2-binary requests python-jwt bcrypt pypdf werkzeug python-json-logger redis

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
ENV PYTHONDONTWRITEBYTECODE=1

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command for development
CMD ["poetry", "run", "python", "src/api.py"]

# ============================================================================
# Production Stage - Final runtime image
# ============================================================================
FROM base AS production
# Force rebuild

# Copy installed dependencies from dependencies stage
COPY --from=dependencies --chown=app:app /home/app/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies --chown=app:app /home/app/.local/bin /usr/local/bin

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

# Run the application directly
CMD ["poetry", "run", "python", "src/api.py"]
