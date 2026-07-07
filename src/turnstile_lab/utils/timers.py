import time


def now_ts() -> float:
    return time.time()


def now_unix() -> int:
    return int(time.time())


def elapsed_seconds(start_time: float, precision: int = 3) -> float:
    return round(time.time() - start_time, precision)


def elapsed_milliseconds(start_time: float) -> int:
    return round((time.time() - start_time) * 1000)