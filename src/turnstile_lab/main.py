import argparse

from turnstile_lab.config import AppConfig, validate_config
from turnstile_lab.logging_conf import setup_logging
from turnstile_lab.api.app import create_app


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="Turnstile Browser Lab")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5072)
    parser.add_argument("--debug", action="store_true")

    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--browser-type", type=str, default="chromium")
    parser.add_argument("--thread-count", type=int, default=4)
    parser.add_argument("--proxy", action="store_true")

    parser.add_argument("--useragent", type=str)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--browser", type=str)
    parser.add_argument("--version", type=str)
    parser.add_argument("--preheat-url", type=str)

    args = parser.parse_args()

    return AppConfig(
        host=args.host,
        port=args.port,
        debug=args.debug,
        headless=not args.no_headless,
        browser_type=args.browser_type,
        thread_count=args.thread_count,
        proxy_support=args.proxy,
        useragent=args.useragent,
        use_random_config=args.random,
        browser_name=args.browser,
        browser_version=args.version,
        preheat_url=args.preheat_url,
    )


def main() -> None:
    config = parse_args()
    validate_config(config)

    logger = setup_logging(debug=config.debug)
    logger.info("Starting Turnstile Browser Lab")

    app = create_app(config)
    app.run(host=config.host, port=config.port)


if __name__ == "__main__":
    main()