from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 5072
    debug: bool = False

    headless: bool = True
    browser_type: str = "chromium"
    thread_count: int = 4
    proxy_support: bool = False

    useragent: Optional[str] = None
    use_random_config: bool = False
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None

    cache_ttl: int = 3600
    result_ttl_days: int = 7

    preheat_url: Optional[str] = None


ALLOWED_BROWSERS = {"chromium", "chrome", "msedge", "camoufox"}


def validate_config(config: AppConfig) -> None:
    if config.browser_type not in ALLOWED_BROWSERS:
        raise ValueError(f"Unsupported browser_type: {config.browser_type}")

    if config.thread_count < 1:
        raise ValueError("thread_count must be >= 1")

    if not (1 <= config.port <= 65535):
        raise ValueError("port must be between 1 and 65535")