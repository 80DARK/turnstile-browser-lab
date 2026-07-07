import hashlib


def md5_text(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def build_cache_key(*parts: str) -> str:
    normalized = [part.strip() for part in parts]
    return "_".join(normalized)


def build_url_cache_key(prefix: str, url: str) -> str:
    return f"{prefix}_{md5_text(url)}"


def build_plate_url_cache_key(placa: str, url: str) -> str:
    return build_url_cache_key(placa.strip().upper(), url)
