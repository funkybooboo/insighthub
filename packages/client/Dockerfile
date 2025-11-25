# syntax=docker/dockerfile:1.4

# ============================================================================
# Base Stage - Common dependencies for all stages
# ============================================================================
FROM oven/bun:1.3.3-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
RUN groupadd -r app && useradd -r -g app -m app
WORKDIR /app
RUN chown -R app:app /app

# ============================================================================
# Dependencies Stage - Install node modules
# ============================================================================
FROM base AS dependencies

# Copy package files
COPY --chown=app:app packages/client/package.json packages/client/bun.lock ./

# Copy shared TypeScript package
COPY --chown=app:app packages/shared/typescript/ ./shared-typescript/

# Build shared TypeScript package
USER app
WORKDIR /app/shared-typescript
RUN bun install && bun run build

# Return to main app directory
WORKDIR /app

	# Install dependencies
	RUN bun install

# ============================================================================
# Development Stage - For local development with hot-reload
# ============================================================================
FROM dependencies AS development

# Copy application code (excluding shared-typescript which is already handled)
COPY --chown=app:app packages/client/.storybook ./storybook/
COPY --chown=app:app packages/client/cypress ./cypress/
COPY --chown=app:app packages/client/src ./src/
COPY --chown=app:app packages/client/public ./public/
COPY --chown=app:app packages/client/*.json ./
COPY --chown=app:app packages/client/*.ts ./
COPY --chown=app:app packages/client/*.js ./
COPY --chown=app:app packages/client/*.html ./
COPY --chown=app:app packages/client/*.conf ./
COPY --chown=app:app packages/client/*.sh ./
COPY --chown=app:app packages/client/*.md ./
COPY --chown=app:app packages/client/.env.example ./
COPY --chown=app:app packages/client/.dockerignore ./
COPY --chown=app:app packages/client/.gitignore ./
COPY --chown=app:app packages/client/.prettierignore ./
COPY --chown=app:app packages/client/.prettierrc ./

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

# Copy application code (excluding shared-typescript which is already handled)
COPY --chown=app:app packages/client/.storybook ./storybook/
COPY --chown=app:app packages/client/cypress ./cypress/
COPY --chown=app:app packages/client/src ./src/
COPY --chown=app:app packages/client/public ./public/
COPY --chown=app:app packages/client/*.json ./
COPY --chown=app:app packages/client/*.ts ./
COPY --chown=app:app packages/client/*.js ./
COPY --chown=app:app packages/client/*.html ./
COPY --chown=app:app packages/client/*.conf ./
COPY --chown=app:app packages/client/*.sh ./
COPY --chown=app:app packages/client/*.md ./
COPY --chown=app:app packages/client/.env.example ./
COPY --chown=app:app packages/client/.dockerignore ./
COPY --chown=app:app packages/client/.gitignore ./
COPY --chown=app:app packages/client/.prettierignore ./
COPY --chown=app:app packages/client/.prettierrc ./

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

# Copy nginx configuration
COPY --chown=nginx:nginx packages/client/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx packages/client/default.conf /etc/nginx/conf.d/default.conf

# Copy and set permissions for entrypoint
COPY --chown=nginx:nginx --chmod=755 packages/client/docker-entrypoint.sh /usr/local/bin/

# Create directory for runtime config and ensure nginx can write to it
RUN mkdir -p /usr/share/nginx/html && chown -R nginx:nginx /usr/share/nginx/html \
    && mkdir -p /tmp/nginx && chown -R nginx:nginx /tmp/nginx \
    && mkdir -p /var/cache/nginx/client_temp \
    && mkdir -p /var/cache/nginx/proxy_temp \
    && mkdir -p /var/cache/nginx/fastcgi_temp \
    && mkdir -p /var/cache/nginx/uwsgi_temp \
    && mkdir -p /var/cache/nginx/scgi_temp \
    && chown -R nginx:nginx /var/cache/nginx \
    && chmod -R 755 /var/cache/nginx \
    && mkdir -p /var/run && chown -R nginx:nginx /var/run \
    && mkdir -p /var/log/nginx && chown -R nginx:nginx /var/log/nginx

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
