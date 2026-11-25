import time
from typing import Any


class QueryCache:

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[Any, float]] = {}

        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:

        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        value, created_at = entry

        if time.time() - created_at >= self.ttl_seconds:
            self._cache.pop(key, None)
            self._misses += 1
            return None

        self._hits += 1
        return value

    def set(self, key: str, value: Any) -> None:

        self._cache[key] = (value, time.time())

    def delete(self, key: str) -> None:

        self._cache.pop(key, None)

    def clear(self) -> None:

        self._cache.clear()

    def stats(self) -> dict[str, int]:

        return {
            "hits": self._hits,
            "misses": self._misses,
            "entries": len(self._cache),
        }