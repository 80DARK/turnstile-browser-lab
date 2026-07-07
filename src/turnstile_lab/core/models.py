from dataclasses import dataclass, field
from typing import Any, Optional
import time


@dataclass(slots=True)
class BrowserProfile:
    browser_name: str
    browser_version: str
    useragent: Optional[str] = None
    sec_ch_ua: str = ""


@dataclass(slots=True)
class BrowserSession:
    index: int
    browser: Any
    context: Any
    page: Any
    profile: BrowserProfile


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    task_type: str
    status: str
    created_at: int = field(default_factory=lambda: int(time.time()))
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)