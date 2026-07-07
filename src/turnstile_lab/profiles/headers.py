from typing import Optional


def build_extra_headers(sec_ch_ua: Optional[str] = None) -> dict[str, str]:
    headers: dict[str, str] = {}

    if sec_ch_ua:
        headers["sec-ch-ua"] = sec_ch_ua

    return headers