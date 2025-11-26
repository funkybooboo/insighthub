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

# Simple startup - let the application handle database connections
log "Starting Flask application..."

# Start the application
log "Starting Flask server on ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-8000}..."
log "Environment: ${FLASK_ENV:-production}"

# Execute the command passed to the container
exec "$@"
