import asyncio

from turnstile_lab.config import AppConfig
from turnstile_lab.core.models import BrowserProfile, BrowserSession
from turnstile_lab.profiles.browser_profiles import browser_config
from turnstile_lab.profiles.headers import build_extra_headers


class BrowserPool:
    def __init__(self, config: AppConfig, logger):
        self.config = config
        self.logger = logger
        self.queue: asyncio.Queue[BrowserSession] = asyncio.Queue()
        self.playwright = None
        self.started = False

    async def start(self) -> None:
        if self.started:
            return

        try:
            from patchright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "patchright is required to start the browser pool. "
                "Install project dependencies with 'pip install -e .[dev]'."
            ) from exc

        self.playwright = await async_playwright().start()

        for index in range(1, self.config.thread_count + 1):
            profile = self._build_profile()
            session = await self._create_session(index, profile)
            await self.queue.put(session)

        self.started = True
        self.logger.info(f"Browser pool initialized with {self.queue.qsize()} sessions")

    def _build_profile(self) -> BrowserProfile:
        if self.config.useragent:
            return BrowserProfile(
                browser_name=self.config.browser_name or self.config.browser_type,
                browser_version=self.config.browser_version or "custom",
                useragent=self.config.useragent,
                sec_ch_ua="",
            )

        if self.config.browser_name and self.config.browser_version:
            cfg = browser_config.get_browser_config(
                self.config.browser_name,
                self.config.browser_version,
            )
            if cfg:
                useragent, sec_ch_ua = cfg
                return BrowserProfile(
                    browser_name=self.config.browser_name,
                    browser_version=self.config.browser_version,
                    useragent=useragent,
                    sec_ch_ua=sec_ch_ua,
                )

        browser, version, useragent, sec_ch_ua = browser_config.get_random_browser_config(
            self.config.browser_type
        )
        return BrowserProfile(
            browser_name=browser,
            browser_version=version,
            useragent=useragent,
            sec_ch_ua=sec_ch_ua,
        )

    async def _create_session(self, index: int, profile: BrowserProfile) -> BrowserSession:
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]

        if profile.useragent:
            browser_args.append(f"--user-agent={profile.useragent}")

        launch_options = {
            "headless": self.config.headless,
            "args": browser_args,
        }

        if self.config.browser_type in {"chrome", "msedge"}:
            launch_options["channel"] = self.config.browser_type

        browser = await self.playwright.chromium.launch(**launch_options)

        context = await browser.new_context(
            user_agent=profile.useragent,
            extra_http_headers=build_extra_headers(profile.sec_ch_ua),
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        if self.config.preheat_url:
            try:
                await page.goto(
                    self.config.preheat_url,
                    wait_until="domcontentloaded",
                    timeout=10000,
                )
                self.logger.debug(f"Browser {index}: preheated successfully")
            except Exception as exc:
                self.logger.warning(f"Browser {index}: preheat failed: {exc}")

        self.logger.info(
            f"Browser {index} initialized with {profile.browser_name} {profile.browser_version}"
        )

        return BrowserSession(
            index=index,
            browser=browser,
            context=context,
            page=page,
            profile=profile,
        )

    async def acquire(self) -> BrowserSession:
        return await self.queue.get()

    async def release(self, session: BrowserSession) -> None:
        await self.queue.put(session)

    async def close(self) -> None:
        while not self.queue.empty():
            session = await self.queue.get()
            try:
                await session.context.close()
            except Exception:
                pass
            try:
                await session.browser.close()
            except Exception:
                pass

        if self.playwright:
            await self.playwright.stop()

        self.started = False
        self.logger.info("Browser pool closed")
