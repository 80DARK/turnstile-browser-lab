import logging
import sys
import time


COLORS = {
    "MAGENTA": "\033[35m",
    "BLUE": "\033[34m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "RED": "\033[31m",
    "RESET": "\033[0m",
}


class CustomLogger(logging.Logger):
    @staticmethod
    def format_message(level: str, color: str, message: str) -> str:
        timestamp = time.strftime("%H:%M:%S")
        return f"[{timestamp}] [{COLORS.get(color)}{level}{COLORS.get('RESET')}] -> {message}"

    def debug(self, message, *args, **kwargs):
        super().debug(self.format_message("DEBUG", "MAGENTA", str(message)), *args, **kwargs)

    def info(self, message, *args, **kwargs):
        super().info(self.format_message("INFO", "BLUE", str(message)), *args, **kwargs)

    def success(self, message, *args, **kwargs):
        super().info(self.format_message("SUCCESS", "GREEN", str(message)), *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        super().warning(self.format_message("WARNING", "YELLOW", str(message)), *args, **kwargs)

    def error(self, message, *args, **kwargs):
        super().error(self.format_message("ERROR", "RED", str(message)), *args, **kwargs)


def setup_logging(debug: bool = False) -> CustomLogger:
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger("turnstile_lab")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    return logger  # type: ignore