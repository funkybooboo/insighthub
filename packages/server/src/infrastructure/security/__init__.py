"""Security infrastructure."""

from .rate_limit_decorator import require_rate_limit

__all__ = ["require_rate_limit"]
