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
            await self._wait_for_security_check(session)
            await self._refresh_plate_events(session)
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
            await self._type_plate_value(session, placa)
        except Exception:
            await session.page.goto(url, wait_until="domcontentloaded", timeout=5000)
            await self._type_plate_value(session, placa)

    async def _type_plate_value(self, session: BrowserSession, placa: str) -> None:
        await session.page.wait_for_selector(SUNARP_PLATE_INPUT, timeout=5000)
        await session.page.click(SUNARP_PLATE_INPUT, timeout=1000)
        await session.page.press(SUNARP_PLATE_INPUT, "Control+A")
        await session.page.press(SUNARP_PLATE_INPUT, "Backspace")
        await session.page.type(SUNARP_PLATE_INPUT, placa, delay=80)
        await self._refresh_plate_events(session)

    async def _refresh_plate_events(self, session: BrowserSession) -> None:
        await session.page.dispatch_event(SUNARP_PLATE_INPUT, "input")
        await session.page.dispatch_event(SUNARP_PLATE_INPUT, "keyup")
        await session.page.dispatch_event(SUNARP_PLATE_INPUT, "change")
        await session.page.dispatch_event(SUNARP_PLATE_INPUT, "blur")

    async def _wait_for_security_check(self, session: BrowserSession) -> None:
        try:
            await session.page.wait_for_function(
                """
                () => {
                    const tokenElement = document.querySelector(
                        '[name="cf-turnstile-response"], [name="g-recaptcha-response"]'
                    );
                    const token = tokenElement?.value || tokenElement?.textContent || "";
                    const button = document.querySelector(
                        'button.ant-btn-primary, button[type="submit"], input[type="submit"]'
                    );

                    return token.trim().length > 10 || (button && !button.disabled);
                }
                """,
                timeout=15000,
            )
        except Exception:
            self.logger.debug(
                f"Browser {session.index}: security check wait timed out, trying submit anyway"
            )

    async def _submit(self, session: BrowserSession) -> None:
        last_error = None

        for selector in SUNARP_SUBMIT_SELECTORS:
            try:
                await session.page.wait_for_function(
                    """
                    (selector) => {
                        const element = document.querySelector(selector);
                        return element && !element.disabled;
                    }
                    """,
                    arg=selector,
                    timeout=5000,
                )
                await session.page.click(selector, timeout=2000)
                return
            except Exception as exc:
                last_error = exc

        state = await self._get_form_state(session)
        self.logger.error(f"Browser {session.index}: SUNARP submit blocked: {state}")

        if last_error:
            raise last_error

    async def _get_form_state(self, session: BrowserSession) -> dict[str, Any]:
        try:
            return await session.page.evaluate(
                """
                () => {
                    const plate = document.querySelector('input#nroPlaca');
                    const tokenElement = document.querySelector(
                        '[name="cf-turnstile-response"], [name="g-recaptcha-response"]'
                    );
                    const button = document.querySelector(
                        'button.ant-btn-primary, button[type="submit"], input[type="submit"]'
                    );
                    const cfText = Array.from(document.querySelectorAll('iframe, div, span'))
                        .map((element) => element.innerText || element.getAttribute('title') || '')
                        .filter(Boolean)
                        .join(' ')
                        .slice(0, 300);

                    const token = tokenElement?.value || tokenElement?.textContent || "";

                    return {
                        plateValue: plate?.value || null,
                        tokenLength: token.trim().length,
                        buttonText: button?.innerText || button?.value || null,
                        buttonDisabled: button ? Boolean(button.disabled) : null,
                        buttonClass: button?.className || null,
                        pageText: cfText,
                    };
                }
                """
            )
        except Exception as exc:
            return {"error": str(exc)}

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
