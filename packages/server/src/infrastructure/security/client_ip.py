"""Client IP extraction utilities."""

from typing import Optional

# Flask-dependent imports
try:
    from flask import Request

    _flask_available = True
except ImportError:
    _flask_available = False
    Request = None  # type: ignore


def get_client_ip(request: Optional["Request"] = None) -> str:
    """
    Extract the real client IP address from the request.

    Handles various proxy scenarios:
    - Direct connection: uses request.remote_addr
    - Behind single proxy: checks X-Forwarded-For header
    - Behind multiple proxies: takes first IP from X-Forwarded-For
    - Cloudflare/other CDNs: checks CF-Connecting-IP header

    Args:
        request: Flask request object (optional, will try to import if not provided)

    Returns:
        Client IP address as string, or "unknown" if unable to determine
    """
    if not _flask_available:
        return "unknown"

    # If no request provided, try to get from Flask globals
    if request is None:
        try:
            from flask import request as flask_request

            request = flask_request
        except (ImportError, RuntimeError):
            return "unknown"

    if not request:
        return "unknown"

    # Try various headers in order of preference
    ip_sources = [
        # Cloudflare
        request.headers.get("CF-Connecting-IP"),
        # Standard proxy header (take first IP if comma-separated)
        request.headers.get("X-Forwarded-For"),
        # Other proxy headers
        request.headers.get("X-Real-IP"),
        request.headers.get("X-Forwarded"),
        request.headers.get("Forwarded-For"),
        request.headers.get("Forwarded"),
        # Direct connection
        request.remote_addr,
    ]

    for ip_source in ip_sources:
        if ip_source:
            # Handle comma-separated values (multiple proxies)
            ip = ip_source.split(",")[0].strip()

            # Validate IP format (basic check)
            if _is_valid_ip(ip):
                return ip

    return "unknown"


def _is_valid_ip(ip: str) -> bool:
    """
    Basic validation for IP address format.

    Args:
        ip: IP address string to validate

    Returns:
        True if valid IPv4 or IPv6 format, False otherwise
    """
    import re

    # IPv4 pattern
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ipv4_pattern, ip):
        # Check that each octet is 0-255
        try:
            octets = [int(octet) for octet in ip.split(".")]
            return all(0 <= octet <= 255 for octet in octets)
        except ValueError:
            return False

    # IPv6 pattern (simplified)
    ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    if re.match(ipv6_pattern, ip):
        return True

    # IPv6 compressed pattern (simplified)
    ipv6_compressed_pattern = r"^([0-9a-fA-F]{1,4}:)*:[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4})*$"
    if re.match(ipv6_compressed_pattern, ip):
        return True

    return False
