from typing import Optional


class NoOpCache(Cache):
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    def get(self, key: str) -> Optional[Any]:
        return None

    def delete(self, key: str) -> None:
        pass

    def clear(self) -> None:
        pass
