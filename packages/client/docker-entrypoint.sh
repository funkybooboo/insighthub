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
if [ -n "$NGINX_PORT" ]; then
    log "Configuring nginx to listen on port $NGINX_PORT"

    if [ -f /etc/nginx/conf.d/default.conf ]; then
        sed -i "s/listen       80;/listen       $NGINX_PORT;/" /etc/nginx/conf.d/default.conf
    else
        warn "Could not find nginx configuration file"
    fi
fi

# Start nginx
log "Starting nginx web server..."

# Execute the command passed to the container
exec "$@"
