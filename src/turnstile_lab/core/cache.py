import time
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._data: dict[str, dict[str, Any]] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = {
            "value": value,
            "timestamp": time.time(),
        }

    def get(self, key: str) -> Optional[Any]:
        item = self._data.get(key)
        if not item:
            return None

        if time.time() - item["timestamp"] > self.ttl_seconds:
            self._data.pop(key, None)
            return None

        return item["value"]

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def cleanup(self) -> int:
        now = time.time()
        expired = [
            key for key, value in self._data.items()
            if now - value["timestamp"] > self.ttl_seconds
        ]
        for key in expired:
            self._data.pop(key, None)
        return len(expired)

    def __len__(self) -> int:
        return len(self._data)