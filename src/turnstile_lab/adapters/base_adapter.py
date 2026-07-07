from abc import ABC, abstractmethod
from typing import Any

from turnstile_lab.core.models import BrowserSession


class BaseAdapter(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    async def run(self, session: BrowserSession, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError