import re
from typing import Optional


PLATE_CLEANUP_PATTERN = re.compile(r"[\s\-\.]")


def normalize_plate(placa: str) -> str:
    placa = placa.upper().strip()
    placa = PLATE_CLEANUP_PATTERN.sub("", placa)
    return placa


def is_valid_plate(placa: str) -> bool:
    normalized = normalize_plate(placa)
    return normalized.isalnum() and 5 <= len(normalized) <= 8


def validate_plate(placa: str) -> tuple[bool, str]:
    normalized = normalize_plate(placa)
    return is_valid_plate(normalized), normalized


def require_non_empty(value: Optional[str], field_name: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()