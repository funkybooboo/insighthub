FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files
COPY pyproject.toml poetry.toml ./

# Install dependencies (no dev dependencies in production)
RUN poetry install --no-root --only main

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Install the project
RUN poetry install --only-root

# Expose port (adjust as needed)
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "python", "src/hello.py"]
