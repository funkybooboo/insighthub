# syntax=docker/dockerfile:1.4

# ============================================================================
# Base Stage - Common dependencies for all stages
# ============================================================================
FROM oven/bun:1.1.38-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
RUN groupadd -r app && useradd -r -g app -m app
WORKDIR /app

# ============================================================================
# Dependencies Stage - Install node modules
# ============================================================================
FROM base AS dependencies

# Copy package files
COPY --chown=app:app package.json bun.lockb ./

# Install dependencies
USER app
RUN bun install --frozen-lockfile

# ============================================================================
# Development Stage - For local development with hot-reload
# ============================================================================
FROM dependencies AS development

# Copy application code
COPY --chown=app:app . .

# Expose Vite dev server port
EXPOSE 5173

# Health check for Vite dev server
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

# Set environment for development
ENV NODE_ENV=development

# Use non-root user
USER app

# Default command for development (Vite with hot-reload)
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

# ============================================================================
# Builder Stage - Build production assets
# ============================================================================
FROM dependencies AS builder

# Copy application code
COPY --chown=app:app . .

# Switch to app user for build
USER app

# Build the application
RUN bun run build

# ============================================================================
# Production Stage - Serve with nginx
# ============================================================================
FROM nginx:1.27-alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Create nginx user and group if they don't exist
RUN addgroup -g 101 -S nginx 2>/dev/null || true \
    && adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx 2>/dev/null || true

# Copy built assets from builder
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Copy nginx configuration (optional - customize as needed)
# COPY --chown=nginx:nginx nginx.conf /etc/nginx/nginx.conf

# Copy and set permissions for entrypoint
COPY --chown=nginx:nginx --chmod=755 docker-entrypoint.sh /usr/local/bin/

# Create directory for runtime config
RUN mkdir -p /usr/share/nginx/html && chown -R nginx:nginx /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Set environment
ENV NGINX_PORT=80

# Use non-root user
USER nginx

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["nginx", "-g", "daemon off;"]
