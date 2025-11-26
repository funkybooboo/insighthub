"""Security infrastructure."""

from .input_sanitizer import InputSanitizer
from .security_logger import log_security_event

# Flask-dependent imports
try:
    from .rate_limit_decorator import require_rate_limit
    _flask_available = True
except ImportError:
    _flask_available = False
    require_rate_limit = None  # type: ignore

__all__ = [
    "InputSanitizer",
    "log_security_event"
]

if _flask_available:
    __all__.append("require_rate_limit")

# Import client IP utility
from .client_ip import get_client_ip
__all__.append("get_client_ip")