#!/bin/bash
set -e

echo "Starting InsightHub Server..."

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
export MAX_RETRIES=30
export RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if poetry run python -c "
import sys
try:
    import psycopg2
    conn = psycopg2.connect('${DATABASE_URL}')
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "PostgreSQL is unavailable (attempt $RETRY_COUNT/$MAX_RETRIES) - sleeping"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Could not connect to PostgreSQL after $MAX_RETRIES attempts"
    exit 1
fi

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head
echo "Migrations completed!"

# Initialize database (create tables, etc.)
echo "Initializing database..."
poetry run python -c "from src.infrastructure.database import init_db; init_db()"
echo "Database initialized!"

# Start the Flask API server with Socket.IO
echo "Starting Flask server on ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-8000}..."
exec poetry run python src/api.py
