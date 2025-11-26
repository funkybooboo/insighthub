"""Security infrastructure."""

from .client_ip import get_client_ip
from .input_sanitizer import InputSanitizer
from .security_logger import log_security_event

# Flask-dependent imports
try:
    from .rate_limit_decorator import require_rate_limit

    _flask_available = True
except ImportError:
    _flask_available = False
    require_rate_limit = None  # type: ignore

__all__ = ["InputSanitizer", "log_security_event", "get_client_ip"]

if _flask_available:
    __all__.append("require_rate_limit")
