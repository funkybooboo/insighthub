"""Lightweight Redis-backed cache shared library."""
from __future__ import annotations

from typing import Any, Optional
import json
import os

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class CacheInterface:
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        raise NotImplementedError
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    def delete(self, key: str) -> None:
        raise NotImplementedError
    def clear(self) -> None:
        raise NotImplementedError


class NoOpCache(CacheInterface):
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass
    def get(self, key: str) -> Optional[Any]:
        return None
    def delete(self, key: str) -> None:
        pass
    def clear(self) -> None:
        pass


class RedisCache(CacheInterface):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None, default_ttl: Optional[int] = None) -> None:
        self._enabled = redis is not None
        self._default_ttl = default_ttl
        self._client = None
        self.host = host; self.port = port; self.db = db; self.password = password
        if self._enabled:
            self._client = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)

    def _ensure(self) -> bool:
        if not self._enabled:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self._ensure():
            return
        payload = json.dumps(value)
        used_ttl = ttl if ttl is not None else self._default_ttl
        if used_ttl:
            self._client.setex(key, int(used_ttl), payload)
        else:
            self._client.set(key, payload)

    def get(self, key: str) -> Optional[Any]:
        if not self._ensure():
            return None
        raw = self._client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return raw

    def delete(self, key: str) -> None:
        if not self._ensure():
            return
        self._client.delete(key)

    def clear(self) -> None:
        if not self._enabled:
            return
        if self._client:
            self._client.flushdb()

    def __enter__(self) -> "RedisCache":
        self._ensure()
        return self

    def __exit__(self, exc_type, exc, tb):
        pass
