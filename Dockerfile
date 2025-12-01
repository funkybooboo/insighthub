FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry
ENV PATH="/usr/local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev dependencies in production)
RUN poetry install --no-root --no-dev

# Copy application code
COPY src/ ./src/
COPY infra/migrations/ ./infra/migrations/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create directory for file uploads (if using filesystem storage)
RUN mkdir -p /app/uploads

# Default command shows help
CMD ["poetry", "run", "python", "-m", "src.main", "--help"]
