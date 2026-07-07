from turnstile_lab.core.models import BrowserSession


class BrowserSessionManager:
    def __init__(self, session: BrowserSession):
        self.session = session

    async def goto(self, url: str, timeout: int = 30000) -> None:
        await self.session.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=timeout,
        )

    async def reset_page(self, url: str, timeout: int = 5000) -> None:
        try:
            await self.session.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=timeout,
            )
        except Exception:
            pass

    async def close(self) -> None:
        try:
            await self.session.context.close()
        except Exception:
            pass

        try:
            await self.session.browser.close()
        except Exception:
            pass