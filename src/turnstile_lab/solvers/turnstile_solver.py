import asyncio
import time
from typing import Any

from turnstile_lab.core.models import BrowserSession
from turnstile_lab.solvers.base_solver import BaseSolver


class TurnstileSolver(BaseSolver):
    async def solve(self, session: BrowserSession, payload: dict[str, Any]) -> dict[str, Any]:
        url = payload["url"]
        sitekey = payload.get("sitekey")
        action = payload.get("action")
        cdata = payload.get("cdata")

        start_time = time.time()

        try:
            await session.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            await asyncio.sleep(3)

            token = await self._extract_token(session)
            elapsed_time = round(time.time() - start_time, 3)

            if token:
                self.logger.success(
                    f"Browser {session.index}: captcha solved in {elapsed_time}s"
                )
                return {
                    "status": "ready",
                    "value": token,
                    "elapsed_time": elapsed_time,
                    "url": url,
                    "sitekey": sitekey,
                    "action": action,
                    "cdata": cdata,
                }

            self.logger.error(f"Browser {session.index}: failed to solve captcha")
            return {
                "status": "error",
                "value": "CAPTCHA_FAIL",
                "elapsed_time": elapsed_time,
                "url": url,
                "sitekey": sitekey,
                "action": action,
                "cdata": cdata,
            }

        except Exception as exc:
            elapsed_time = round(time.time() - start_time, 3)
            self.logger.error(f"Browser {session.index}: error: {exc}")
            return {
                "status": "error",
                "value": "CAPTCHA_FAIL",
                "elapsed_time": elapsed_time,
                "error": str(exc),
                "url": url,
                "sitekey": sitekey,
                "action": action,
                "cdata": cdata,
            }

    async def _extract_token(self, session: BrowserSession) -> str | None:
        for _ in range(30):
            try:
                token = await session.page.evaluate("""
                    () => {
                        const selectors = [
                            'input[name="cf-turnstile-response"]',
                            'textarea[name="cf-turnstile-response"]',
                            '[name="cf-turnstile-response"]',
                            'input[name="g-recaptcha-response"]',
                            'textarea[name="g-recaptcha-response"]'
                        ];

                        for (const selector of selectors) {
                            const element = document.querySelector(selector);
                            if (!element) continue;

                            const value = element.value || element.textContent || "";
                            if (value.trim().length > 10) return value.trim();
                        }

                        if (window.turnstileToken && String(window.turnstileToken).length > 10) {
                            return String(window.turnstileToken);
                        }

                        return null;
                    }
                """)
                if token:
                    return token
            except Exception:
                pass

            await asyncio.sleep(1)

        return None
