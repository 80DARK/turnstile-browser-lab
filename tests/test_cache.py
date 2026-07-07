import time
import pytest

from turnstile_lab.utils.hashes import md5_text, build_plate_url_cache_key
from turnstile_lab.storage.memory_store import MemoryStore


def test_md5_text_is_deterministic():
    value = "https://consultavehicular.sunarp.gob.pe/"
    assert md5_text(value) == md5_text(value)
    assert md5_text(value) != md5_text(value + "/x")


def test_build_plate_url_cache_key():
    key = build_plate_url_cache_key("ABC123", "https://consultavehicular.sunarp.gob.pe/")
    assert key.startswith("ABC123_")
    assert len(key.split("_", 1)[1]) == 32


@pytest.mark.asyncio
async def test_memory_store_save_and_load():
    store = MemoryStore()
    await store.init_db()

    await store.save_result("task-1", "turnstile", {"status": "ready", "value": "token-123"})
    result = await store.load_result("task-1")

    assert result["status"] == "ready"
    assert result["value"] == "token-123"


@pytest.mark.asyncio
async def test_memory_store_cleanup_old_results():
    store = MemoryStore()
    await store.init_db()

    await store.save_result("task-old", "turnstile", {"status": "ready"})
    store._data["task-old"]["created_at"] = time.time() - (8 * 86400)

    deleted = await store.cleanup_old_results(days_old=7)

    assert deleted == 1
    assert await store.load_result("task-old") is None