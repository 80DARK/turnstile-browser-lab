import time
from typing import Any, Optional


class MemoryStore:
    def __init__(self):
        self._data: dict[str, dict[str, Any]] = {}

    async def init_db(self) -> None:
        return None

    async def save_result(self, task_id: str, task_type: str, data: dict[str, Any] | str) -> None:
        self._data[task_id] = {
            "type": task_type,
            "data": data,
            "created_at": time.time(),
        }

    async def load_result(self, task_id: str) -> Optional[dict[str, Any] | str]:
        item = self._data.get(task_id)
        if not item:
            return None
        return item["data"]

    async def cleanup_old_results(self, days_old: int = 7) -> int:
        max_age = days_old * 86400
        now = time.time()

        keys_to_delete = [
            key for key, value in self._data.items()
            if now - value["created_at"] > max_age
        ]

        for key in keys_to_delete:
            self._data.pop(key, None)

        return len(keys_to_delete)