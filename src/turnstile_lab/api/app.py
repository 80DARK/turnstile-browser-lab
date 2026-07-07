import asyncio
from quart import Quart

from turnstile_lab.config import AppConfig
from turnstile_lab.core.browser_pool import BrowserPool
from turnstile_lab.core.task_manager import TaskManager
from turnstile_lab.api.routes_health import health_bp
from turnstile_lab.api.routes_tasks import tasks_bp


def create_app(config: AppConfig) -> Quart:
    app = Quart(__name__)

    app.config["APP_CONFIG"] = config
    app.config["LOGGER"] = None
    app.config["BROWSER_POOL"] = None
    app.config["TASK_MANAGER"] = None
    app.config["CLEANUP_TASK"] = None

    register_blueprints(app)
    register_lifecycle(app)

    return app


def register_blueprints(app: Quart) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(tasks_bp)


def register_lifecycle(app: Quart) -> None:
    @app.before_serving
    async def startup() -> None:
        from turnstile_lab.logging_conf import setup_logging

        logger = setup_logging(debug=app.config["APP_CONFIG"].debug)
        app.config["LOGGER"] = logger

        config: AppConfig = app.config["APP_CONFIG"]

        logger.info("Starting API application")

        browser_pool = BrowserPool(config=config, logger=logger)
        await browser_pool.start()

        task_manager = TaskManager(
            browser_pool=browser_pool,
            logger=logger,
            result_ttl_days=config.result_ttl_days,
            cache_ttl=config.cache_ttl,
        )
        await task_manager.startup()

        app.config["BROWSER_POOL"] = browser_pool
        app.config["TASK_MANAGER"] = task_manager
        app.config["CLEANUP_TASK"] = asyncio.create_task(periodic_cleanup(app))

        logger.info("Application startup completed")

    @app.after_serving
    async def shutdown() -> None:
        logger = app.config.get("LOGGER")
        cleanup_task = app.config.get("CLEANUP_TASK")
        browser_pool = app.config.get("BROWSER_POOL")

        if cleanup_task:
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass

        if browser_pool:
            await browser_pool.close()

        if logger:
            logger.info("Application shutdown completed")


async def periodic_cleanup(app: Quart) -> None:
    while True:
        try:
            await asyncio.sleep(3600)

            task_manager = app.config.get("TASK_MANAGER")
            logger = app.config.get("LOGGER")

            if not task_manager or not logger:
                continue

            deleted_count = await task_manager.cleanup_results()
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old results")

        except asyncio.CancelledError:
            logger = app.config.get("LOGGER")
            if logger:
                logger.info("Periodic cleanup task cancelled")
            raise

        except Exception as exc:
            logger = app.config.get("LOGGER")
            if logger:
                logger.error(f"Error during periodic cleanup: {exc}")
