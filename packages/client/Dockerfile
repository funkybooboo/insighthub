# Base stage with dependencies
FROM oven/bun:1 AS base

# Install make
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files and Makefile
COPY package.json bun.lock* Makefile ./

# Install dependencies using make
RUN make install

# Development stage
FROM base AS development

# Copy all source files
COPY . .

# Quality check stage - runs make check
FROM development AS quality

# Run all checks (format-check, lint, build)
RUN make check

# Build stage
FROM base AS builder

# Copy all source files
COPY . .

# Build the application using make
RUN make build

# Production stage
FROM nginx:alpine AS production

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration (if you have one)
# COPY nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 80

# Use entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]
