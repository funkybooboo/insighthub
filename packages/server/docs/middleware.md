# Middleware Documentation

This document describes the middleware stack implemented in InsightHub.

## Overview

The application uses a layered middleware approach for security, logging, monitoring, and request validation. Middleware is applied in a specific order to ensure proper request processing.

## Middleware Stack

The middleware is applied in the following order (from `src/api.py`):

1. **Security Headers Middleware**
2. **Request Validation Middleware**
3. **Rate Limiting Middleware**
4. **Request Logging Middleware**
5. **Performance Monitoring Middleware**

## 1. Security Headers Middleware

**Location**: `src/infrastructure/middleware/security.py`

Adds security headers to all HTTP responses following OWASP best practices.

### Headers Added

- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-XSS-Protection: 1; mode=block` - XSS filter for legacy browsers
- `Content-Security-Policy` - Restricts resource loading
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer info
- `Permissions-Policy` - Disables dangerous browser features
- `Strict-Transport-Security` (Production only) - Forces HTTPS

### Configuration

Security headers are configured with sensible defaults. For custom CSP rules, modify the `_default_config()` method in `SecurityHeadersMiddleware`.

## 2. Request Validation Middleware

**Location**: `src/infrastructure/middleware/validation.py`

Validates incoming requests before they reach business logic.

### Validation Checks

1. **Content-Length Validation**
   - Rejects requests exceeding `MAX_CONTENT_LENGTH`
   - Default: 16MB

2. **Content-Type Validation**
   - Validates Content-Type for POST/PUT/PATCH requests
   - Allowed types: `application/json`, `multipart/form-data`, `text/plain`

3. **JSON Validation**
   - Validates JSON payloads for JSON requests
   - Returns 400 for malformed JSON

4. **Path Traversal Prevention**
   - Detects and blocks path traversal attempts (`../`, `..\\`, etc.)

### Environment Variables

```bash
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

## 3. Rate Limiting Middleware

**Location**: `src/infrastructure/middleware/rate_limiting.py`

Simple in-memory rate limiting per IP address.

### Features

- Per-minute rate limiting
- Per-hour rate limiting
- IP-based tracking (handles proxies via `X-Forwarded-For`)
- Automatic cleanup of old entries
- Health check exemptions

### Configuration

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Response Codes

- `429 Too Many Requests` - Rate limit exceeded
- Response includes `retry_after` field in seconds

### Production Considerations

For production with multiple server instances, consider:
- Redis-backed rate limiting (Flask-Limiter + Redis)
- Shared rate limit state across instances
- More sophisticated algorithms (token bucket, sliding window)

## 4. Request Logging Middleware

**Location**: `src/infrastructure/middleware/logging.py`

Logs all incoming requests and outgoing responses with detailed context.

### Logged Information

**Request Start:**
- Method, path, client IP
- User agent
- User ID (if authenticated)
- Query parameters
- Headers (sanitized)

**Request End:**
- Status code
- Response time (milliseconds)
- Content length

### Sensitive Data Handling

The following headers are redacted from logs:
- `Authorization`
- `Cookie`
- `X-API-Key`

### Configuration

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log  # Optional file logging
```

## 5. Performance Monitoring Middleware

**Location**: `src/infrastructure/middleware/monitoring.py`

Monitors request performance and collects statistics.

### Features

1. **Slow Request Detection**
   - Warns about requests exceeding threshold
   - Default: 1.0 seconds

2. **Endpoint Statistics**
   - Request count per endpoint
   - Average, min, max response times
   - Total processing time

3. **Response Headers**
   - Adds `X-Response-Time` header to all responses

### Configuration

```bash
SLOW_REQUEST_THRESHOLD=1.0  # seconds
ENABLE_PERFORMANCE_STATS=true
```

### Accessing Statistics

Performance statistics are available at the `/metrics` endpoint:

```bash
GET /metrics
```

Response:
```json
{
  "status": "healthy",
  "performance": {
    "GET /api/documents": {
      "count": 150,
      "avg_time": 0.045,
      "min_time": 0.012,
      "max_time": 0.234,
      "total_time": 6.75
    },
    "POST /api/chat": {
      "count": 89,
      "avg_time": 1.234,
      "min_time": 0.567,
      "max_time": 3.456,
      "total_time": 109.826
    }
  }
}
```

## Structured Logging

**Location**: `src/infrastructure/logging_config.py`

### Features

- Request context in all logs (request ID, path, method, IP)
- stdout for INFO and DEBUG messages
- stderr for WARNING, ERROR, and CRITICAL messages
- Configurable log levels
- Third-party library noise reduction
- Container-friendly (12-factor app compliant)

### Log Format

```
[2025-11-11 19:50:00] INFO [module.name] [request-id] [GET /api/endpoint] - Message
```

### Log Streams

- **stdout**: INFO and DEBUG messages
- **stderr**: WARNING, ERROR, and CRITICAL messages

This separation allows log aggregation systems (like Docker, Kubernetes, CloudWatch) to properly categorize and route logs.

### Configuration

```bash
LOG_LEVEL=INFO
```

## CORS Configuration

CORS is configured in `src/api.py` with the following settings:

```python
CORS(
    app,
    origins=["http://localhost:5173", "http://localhost:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)
```

### Configuration

```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

For production, set to your domain:
```bash
CORS_ORIGINS=https://yourdomain.com
```

## Environment-Specific Configuration

### Development (.env)

```bash
LOG_LEVEL=DEBUG
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=2000
SLOW_REQUEST_THRESHOLD=1.0
```

### Production (.env.prod.example)

```bash
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
SLOW_REQUEST_THRESHOLD=2.0
CORS_ORIGINS=https://yourdomain.com
```

### Testing (.env.test)

```bash
LOG_LEVEL=ERROR
RATE_LIMIT_ENABLED=false
ENABLE_PERFORMANCE_STATS=false
```

### Container/Production Log Collection

Logs are written to stdout/stderr for easy collection:

**Docker:**
```bash
docker logs <container-id>
```

**Kubernetes:**
```bash
kubectl logs <pod-name>
```

**Production log aggregation:**
- Use log shippers (Fluentd, Logstash, Filebeat)
- Configure log retention in your orchestration platform
- Route stderr to alerting systems (errors/warnings)

## Best Practices

1. **Security Headers**: Review CSP rules for your specific needs
2. **Rate Limiting**: Adjust limits based on your API usage patterns
3. **Logging**: Use appropriate log levels (DEBUG only in development)
4. **Performance**: Monitor `/metrics` endpoint regularly
5. **CORS**: Use specific origins in production (never use `*`)

## Disabling Middleware

To disable specific middleware:

```bash
# Disable rate limiting
RATE_LIMIT_ENABLED=false

# Disable performance stats collection
ENABLE_PERFORMANCE_STATS=false
```

## Troubleshooting

### High Memory Usage

If rate limiting causes memory issues:
- Reduce `RATE_LIMIT_PER_HOUR` window
- Consider Redis-backed rate limiting
- Monitor with `/metrics` endpoint

### Slow Performance

If middleware overhead is high:
- Disable performance statistics in production
- Use WARNING/ERROR log level in production
- Review slow request threshold

### Rate Limit False Positives

If legitimate users hit rate limits:
- Increase `RATE_LIMIT_PER_MINUTE`
- Check for proxy configuration issues
- Consider authenticated user allowances
