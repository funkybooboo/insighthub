#!/bin/bash
set -e

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[entrypoint]${NC} $1"
}

error() {
    echo -e "${RED}[entrypoint ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[entrypoint WARNING]${NC} $1"
}

log "Starting InsightHub Server..."

# Wait for PostgreSQL to be ready
if [ -n "$DATABASE_URL" ]; then
    log "Waiting for PostgreSQL to be ready..."

    MAX_RETRIES=30
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if poetry run python -c "
import sys
import psycopg2
try:
    conn = psycopg2.connect('${DATABASE_URL}')
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
            log "PostgreSQL is ready!"
            break
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        warn "PostgreSQL is unavailable (attempt $RETRY_COUNT/$MAX_RETRIES) - retrying in 2s..."
        sleep 2
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        error "Could not connect to PostgreSQL after $MAX_RETRIES attempts"
        exit 1
    fi

    # Run database migrations
    log "Running database migrations..."
    if poetry run alembic upgrade head; then
        log "Migrations completed successfully!"
    else
        error "Database migrations failed!"
        exit 1
    fi

    # Initialize database
    log "Initializing database..."
    if poetry run python -c "from src.infrastructure.database import init_db; init_db()"; then
        log "Database initialized successfully!"
    else
        warn "Database initialization had issues (may already be initialized)"
    fi
else
    warn "DATABASE_URL not set - skipping database initialization"
fi

# Start the application
log "Starting Flask server on ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-8000}..."
log "Environment: ${FLASK_ENV:-production}"

# Execute the command passed to the container
exec "$@"
