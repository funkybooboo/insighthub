FROM python:3.11-slim AS base

# Install system dependencies including make
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Development stage with all dependencies
FROM base AS development

# Copy dependency files
COPY pyproject.toml poetry.toml Makefile README.md ./

# Install all dependencies (including dev)
RUN poetry install --no-root

# Copy source code and migrations
COPY src/ ./src/
COPY tests/ ./tests/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Install the project
RUN poetry install --only-root

# Quality check stage - runs make check
FROM development AS quality

# Run all quality checks (format, lint, type-check, test)
RUN make check

# Production stage
FROM base AS production

# Copy dependency files
COPY pyproject.toml poetry.toml Makefile README.md ./

# Install production dependencies using make
RUN poetry install --no-root --only main

# Copy source code and migrations
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Install the project
RUN poetry install --only-root

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Set environment variables for Flask
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8000

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
