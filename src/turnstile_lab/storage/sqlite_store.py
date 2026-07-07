import json
import logging
from typing import Any, Optional, Union

import aiosqlite


DB_PATH = "results.db"

PRAGMA_SETTINGS = [
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA cache_size=10000",
    "PRAGMA temp_store=MEMORY",
    "PRAGMA busy_timeout=30000",
]


async def _apply_pragma_settings(db) -> None:
    for pragma in PRAGMA_SETTINGS:
        await db.execute(pragma)


async def init_db() -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await _apply_pragma_settings(db)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    task_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

            logging.getLogger("turnstile_lab").info("Database initialized")
    except Exception as exc:
        logging.getLogger("turnstile_lab").error(f"Database error: {exc}")
        raise


async def save_result(task_id: str, task_type: str, data: Union[dict[str, Any], str]) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await _apply_pragma_settings(db)

            data_json = json.dumps(data) if isinstance(data, dict) else data

            await db.execute(
                "REPLACE INTO results (task_id, type, data) VALUES (?, ?, ?)",
                (task_id, task_type, data_json),
            )
            await db.commit()

    except Exception as exc:
        logging.getLogger("turnstile_lab").error(f"Error saving result: {exc}")


async def load_result(task_id: str) -> Optional[Union[dict[str, Any], str]]:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await _apply_pragma_settings(db)

            async with db.execute(
                "SELECT data FROM results WHERE task_id = ?",
                (task_id,),
            ) as cursor:
                row = await cursor.fetchone()

            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]

            return None

    except Exception as exc:
        logging.getLogger("turnstile_lab").error(f"Error loading result: {exc}")
        return None


async def cleanup_old_results(days_old: int = 7) -> int:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await _apply_pragma_settings(db)

            async with db.execute(
                f"DELETE FROM results WHERE created_at < datetime('now', '-{days_old} days')"
            ) as cursor:
                deleted_count = cursor.rowcount

            await db.commit()
            return deleted_count or 0

    except Exception as exc:
        logging.getLogger("turnstile_lab").error(f"Error cleaning up: {exc}")
        return 0