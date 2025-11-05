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
COPY pyproject.toml poetry.toml Makefile ./

# Install all dependencies (including dev)
RUN poetry install --no-root

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Install the project
RUN poetry install --only-root

# Quality check stage - runs make check
FROM development AS quality

# Run all quality checks (format, lint, type-check, test)
RUN make check

# Production stage
FROM base AS production

# Copy dependency files
COPY pyproject.toml poetry.toml Makefile ./

# Install production dependencies using make
RUN poetry install --no-root --only main

# Copy source code
COPY src/ ./src/

# Install the project
RUN poetry install --only-root

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "python", "src/hello.py"]
