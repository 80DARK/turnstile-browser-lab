import asyncio
import uuid
from typing import Optional

from turnstile_lab.adapters.sunarp.adapter import SunarpAdapter
from turnstile_lab.core.cache import TTLCache
from turnstile_lab.core.browser_pool import BrowserPool
from turnstile_lab.storage.sqlite_store import (
    init_db,
    save_result,
    load_result,
    cleanup_old_results,
)
from turnstile_lab.solvers.turnstile_solver import TurnstileSolver
from turnstile_lab.utils.hashes import build_plate_url_cache_key
from turnstile_lab.utils.timers import now_unix


class TaskManager:
    def __init__(
        self,
        browser_pool: BrowserPool,
        logger,
        result_ttl_days: int = 7,
        cache_ttl: int = 3600,
    ):
        self.browser_pool = browser_pool
        self.logger = logger
        self.result_ttl_days = result_ttl_days
        self.turnstile_solver = TurnstileSolver(logger)
        self.sunarp_adapter = SunarpAdapter(logger)
        self.cache = TTLCache(ttl_seconds=cache_ttl)
        self.running_tasks: set[asyncio.Task] = set()

    async def startup(self) -> None:
        await init_db()

    async def create_turnstile_task(
        self,
        url: str,
        sitekey: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> str:
        task_id = str(uuid.uuid4())

        await save_result(task_id, "turnstile", {
            "status": "CAPTCHA_NOT_READY",
            "createTime": now_unix(),
            "url": url,
            "sitekey": sitekey,
            "action": action,
            "cdata": cdata,
        })

        task = asyncio.create_task(
            self._run_turnstile_task(
                task_id=task_id,
                url=url,
                sitekey=sitekey,
                action=action,
                cdata=cdata,
            )
        )
        self.running_tasks.add(task)
        task.add_done_callback(self.running_tasks.discard)
        
        return task_id

    async def create_sunarp_task(self, url: str, placa: str) -> str:
        cache_key = build_plate_url_cache_key(placa, url)
        cached_task_id = self.cache.get(cache_key)
        if cached_task_id:
            self.logger.debug(f"SUNARP cache hit for {placa}")
            return cached_task_id

        task_id = str(uuid.uuid4())

        await save_result(task_id, "consulta", {
            "status": "PROCESSING",
            "createTime": now_unix(),
            "url": url,
            "placa": placa,
        })

        self.cache.set(cache_key, task_id)

        task = asyncio.create_task(
            self._run_sunarp_task(
                task_id=task_id,
                url=url,
                placa=placa,
            )
        )
        self.running_tasks.add(task)
        task.add_done_callback(self.running_tasks.discard)

        return task_id

    async def _run_turnstile_task(
        self,
        task_id: str,
        url: str,
        sitekey: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> None:
        session = await self.browser_pool.acquire()

        try:
            result = await self.turnstile_solver.solve(session, {
                "url": url,
                "sitekey": sitekey,
                "action": action,
                "cdata": cdata,
            })

            await save_result(task_id, "turnstile", result)

        except Exception as exc:
            await save_result(task_id, "turnstile", {
                "status": "error",
                "value": "CAPTCHA_FAIL",
                "error": str(exc),
            })
            self.logger.error(f"Task {task_id}: unexpected error: {exc}")

        finally:
            await self.browser_pool.release(session)

    async def _run_sunarp_task(self, task_id: str, url: str, placa: str) -> None:
        session = await self.browser_pool.acquire()

        try:
            result = await self.sunarp_adapter.run(session, {
                "url": url,
                "placa": placa,
            })

            await save_result(task_id, "consulta", result)

        except Exception as exc:
            await save_result(task_id, "consulta", {
                "status": "error",
                "placa": placa,
                "error": str(exc),
            })
            self.logger.error(f"Task {task_id}: unexpected SUNARP error: {exc}")

        finally:
            await self.browser_pool.release(session)

    async def get_result(self, task_id: str):
        return await load_result(task_id)

    async def cleanup_results(self) -> int:
        return await cleanup_old_results(days_old=self.result_ttl_days)
