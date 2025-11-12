#!/bin/sh
set -e

echo "Starting InsightHub Client..."

# Generate runtime configuration if needed
# This allows environment variables to be injected at runtime
if [ -n "$VITE_API_URL" ]; then
    echo "Configuring API URL: $VITE_API_URL"
    cat > /usr/share/nginx/html/config.js <<EOF
window.ENV = {
    API_URL: "${VITE_API_URL}",
    WS_URL: "${VITE_WS_URL:-$VITE_API_URL}"
};
EOF
fi

# Create nginx configuration if NGINX_CONF is set
if [ -n "$NGINX_PORT" ]; then
    echo "Configuring nginx to listen on port $NGINX_PORT"
    sed -i "s/listen       80;/listen       $NGINX_PORT;/" /etc/nginx/conf.d/default.conf
fi

# Start nginx
echo "Starting nginx..."
exec nginx -g "daemon off;"
