from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class SunarpRequest:
    url: str
    placa: str
    sitekey: Optional[str] = None


@dataclass(slots=True)
class SunarpResult:
    status: str
    placa: str
    image_base64: Optional[str] = None
    error: Optional[str] = None