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

# Install dependencies (including dev for hot reload)
RUN poetry install --no-root

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command (can be overridden by docker-compose)
CMD ["/usr/local/bin/poetry", "run", "python", "-m", "src.main"]
