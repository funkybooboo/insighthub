# Re-export shared config for backward compatibility
from shared.config import config

# Backward compatibility - expose individual config values
# These can be removed once all code is updated to use config.*
FLASK_HOST = config.host
FLASK_PORT = config.port
FLASK_DEBUG = config.debug
DATABASE_URL = config.database.url
REDIS_URL = config.redis.url or ""
JWT_SECRET_KEY = config.security.jwt_secret_key
JWT_EXPIRE_MINUTES = config.security.jwt_expire_minutes
CORS_ORIGINS = config.security.cors_origins

# Additional backward compatibility
UPLOAD_FOLDER = config.upload_folder
MAX_CONTENT_LENGTH = config.max_content_length
RATE_LIMIT_ENABLED = config.rate_limit_enabled
RATE_LIMIT_PER_MINUTE = config.rate_limit_per_minute
RATE_LIMIT_PER_HOUR = config.rate_limit_per_hour
LOG_LEVEL = config.log_level
LOG_FORMAT = config.log_format
SLOW_REQUEST_THRESHOLD = config.slow_request_threshold
ENABLE_PERFORMANCE_STATS = config.enable_performance_stats
