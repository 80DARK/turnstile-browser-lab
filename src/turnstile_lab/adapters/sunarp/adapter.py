import asyncio
import base64
from typing import Any

from turnstile_lab.adapters.base_adapter import BaseAdapter
from turnstile_lab.core.models import BrowserSession
from turnstile_lab.adapters.sunarp.selectors import (
    SUNARP_PLATE_INPUT,
    SUNARP_SUBMIT_SELECTORS,
    SUNARP_SUCCESS_SELECTORS,
    SUNARP_IMAGE_SELECTORS,
    SUNARP_CAPTURE_CONTAINERS,
)


class SunarpAdapter(BaseAdapter):
    async def run(self, session: BrowserSession, payload: dict[str, Any]) -> dict[str, Any]:
        url = payload["url"]
        placa = payload["placa"]

        try:
            await self._fill_plate(session, url, placa)
            await self._submit(session)

            found_selector = await self._wait_for_result(session)
            if not found_selector:
                await self._safe_reload(session, url)
                return {
                    "status": "error",
                    "placa": placa,
                    "error": f"No se encontraron resultados para {placa}",
                }

            image_bytes = await self._extract_image_bytes(session)
            if not image_bytes:
                await self._safe_reload(session, url)
                return {
                    "status": "error",
                    "placa": placa,
                    "error": "No se pudo capturar la imagen",
                }

            await self._safe_reload(session, url)

            return {
                "status": "ready",
                "placa": placa,
                "image": base64.b64encode(image_bytes).decode("utf-8"),
            }

        except Exception as exc:
            await self._safe_reload(session, url)
            self.logger.error(f"Browser {session.index}: SUNARP error: {exc}")
            return {
                "status": "error",
                "placa": placa,
                "error": str(exc),
            }

    async def _fill_plate(self, session: BrowserSession, url: str, placa: str) -> None:
        try:
            await session.page.fill(SUNARP_PLATE_INPUT, "", timeout=1000)
            await session.page.fill(SUNARP_PLATE_INPUT, placa, timeout=1000)
        except Exception:
            await session.page.goto(url, wait_until="domcontentloaded", timeout=5000)
            await session.page.fill(SUNARP_PLATE_INPUT, placa, timeout=1000)

    async def _submit(self, session: BrowserSession) -> None:
        last_error = None

        for selector in SUNARP_SUBMIT_SELECTORS:
            try:
                await session.page.click(selector, timeout=2000)
                return
            except Exception as exc:
                last_error = exc

        if last_error:
            raise last_error

    async def _wait_for_result(self, session: BrowserSession) -> str | None:
        for selector in SUNARP_SUCCESS_SELECTORS:
            try:
                await session.page.wait_for_selector(selector, timeout=2000)
                self.logger.debug(
                    f"Browser {session.index}: SUNARP result found with {selector}"
                )
                return selector
            except Exception:
                continue

        return None

    async def _extract_image_bytes(self, session: BrowserSession) -> bytes | None:
        for selector in SUNARP_IMAGE_SELECTORS:
            try:
                img_element = await session.page.query_selector(selector)
                if not img_element:
                    continue

                src = await img_element.get_attribute("src")
                if src and src.startswith("data:image"):
                    base64_data = src.split(",", 1)[1]
                    return base64.b64decode(base64_data)
            except Exception:
                continue

        for selector in SUNARP_CAPTURE_CONTAINERS:
            try:
                container = await session.page.query_selector(selector)
                if container:
                    return await container.screenshot()
            except Exception:
                continue

        return None

    async def _safe_reload(self, session: BrowserSession, url: str) -> None:
        try:
            await session.page.goto(url, wait_until="domcontentloaded", timeout=3000)
        except Exception:
            pass