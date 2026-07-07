from quart import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/")
async def index():
    return {
        "name": "turnstile-browser-lab",
        "status": "ok",
        "docs": {
            "turnstile": "/turnstile?url=...&sitekey=...",
            "consultar": "/consultar?url=...&sitekey=...&placa=ABC123",
            "result": "/result?id=task_id",
            "health": "/health",
        },
    }


@health_bp.get("/health")
async def health():
    config = current_app.config["APP_CONFIG"]

    return jsonify({
        "status": "ok",
        "browser_type": config.browser_type,
        "thread_count": config.thread_count,
        "headless": config.headless,
    })
