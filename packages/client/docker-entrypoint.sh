#!/bin/sh
set -e

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    printf "${GREEN}[entrypoint]${NC} %s\n" "$1"
}

error() {
    printf "${RED}[entrypoint ERROR]${NC} %s\n" "$1" >&2
}

warn() {
    printf "${YELLOW}[entrypoint WARNING]${NC} %s\n" "$1"
}

log "Starting InsightHub Client..."

# Generate runtime configuration for environment variables
# This allows environment variables to be injected at runtime
if [ -n "$VITE_API_URL" ]; then
    log "Configuring API URL: $VITE_API_URL"

    cat > /usr/share/nginx/html/config.js <<EOF
window.ENV = {
    API_URL: "${VITE_API_URL}",
    WS_URL: "${VITE_WS_URL:-$VITE_API_URL}"
};
EOF
fi

# Configure nginx port if specified
# Note: This needs to run as root or with proper permissions
# For now, we skip this in production and use environment variables or config files
if [ -n "$NGINX_PORT" ] && [ "$NGINX_PORT" != "80" ]; then
    warn "Custom NGINX_PORT specified but cannot modify config as non-root user"
    warn "Using default port 80 instead"
fi

# Start nginx
log "Starting nginx web server..."

# Execute the command passed to the container
exec "$@"
