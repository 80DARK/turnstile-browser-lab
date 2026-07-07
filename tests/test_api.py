import pytest

from turnstile_lab.api.app import create_app
from turnstile_lab.config import AppConfig


class DummyLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass


class DummyTaskManager:
    def __init__(self):
        self.created = []

    async def create_turnstile_task(self, url, sitekey, action=None, cdata=None):
        self.created.append({
            "url": url,
            "sitekey": sitekey,
            "action": action,
            "cdata": cdata,
        })
        return "task-123"

    async def create_sunarp_task(self, url, placa):
        self.created.append({
            "url": url,
            "placa": placa,
        })
        return "sunarp-task-123"

    async def get_result(self, task_id):
        return None

    async def cleanup_results(self):
        return 0

    async def startup(self):
        return None


@pytest.fixture
def app():
    config = AppConfig(
        debug=True,
        browser_type="chromium",
        thread_count=2,
        headless=True,
    )
    app = create_app(config)
    app.config["LOGGER"] = DummyLogger()
    app.config["TASK_MANAGER"] = DummyTaskManager()
    return app

@pytest.mark.asyncio
async def test_index_route(app):
    client = app.test_client()
    response = await client.get("/")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["name"] == "turnstile-browser-lab"
    assert data["status"] == "ok"
    assert "turnstile" in data["docs"]


@pytest.mark.asyncio
async def test_health_route(app):
    client = app.test_client()
    response = await client.get("/health")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["browser_type"] == "chromium"
    assert data["thread_count"] == 2
    assert data["headless"] is True


@pytest.mark.asyncio
async def test_turnstile_requires_url_and_sitekey(app):
    client = app.test_client()
    response = await client.get("/turnstile")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 1
    assert data["errorCode"] == "ERROR_WRONG_PAGEURL"


@pytest.mark.asyncio
async def test_turnstile_creates_task(app):
    client = app.test_client()
    response = await client.get("/turnstile?url=https://example.com&sitekey=abc")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 0
    assert data["taskId"] == "task-123"


@pytest.mark.asyncio
async def test_consultar_requires_url_sitekey_and_placa(app):
    client = app.test_client()
    response = await client.get("/consultar")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 1
    assert data["errorCode"] == "ERROR_WRONG_PARAMETERS"


@pytest.mark.asyncio
async def test_consultar_creates_task_with_normalized_plate(app):
    client = app.test_client()
    response = await client.get(
        "/consultar?url=https://sunarp.example&sitekey=abc&placa=abc-123"
    )
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 0
    assert data["taskId"] == "sunarp-task-123"
    assert app.config["TASK_MANAGER"].created[-1]["placa"] == "ABC123"


@pytest.mark.asyncio
async def test_result_processing_when_task_not_ready(app):
    client = app.test_client()
    response = await client.get("/result?id=task-123")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["status"] == "processing"
    
@pytest.mark.asyncio
async def test_result_ready_token(app):
    async def fake_get_result(task_id):
        return {
            "status": "ready",
            "value": "token-xyz",
        }

    app.config["TASK_MANAGER"].get_result = fake_get_result

    client = app.test_client()
    response = await client.get("/result?id=task-123")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 0
    assert data["status"] == "ready"
    assert data["solution"]["token"] == "token-xyz"


@pytest.mark.asyncio
async def test_result_unsolvable(app):
    async def fake_get_result(task_id):
        return {
            "status": "error",
            "value": "CAPTCHA_FAIL",
        }

    app.config["TASK_MANAGER"].get_result = fake_get_result

    client = app.test_client()
    response = await client.get("/result?id=task-123")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["errorId"] == 1
    assert data["errorCode"] == "ERROR_CAPTCHA_UNSOLVABLE"


@pytest.mark.asyncio
async def test_result_ready_sunarp_image(app):
    async def fake_get_result(task_id):
        return {
            "status": "ready",
            "image": "base64-image",
            "placa": "ABC123",
        }

    app.config["TASK_MANAGER"].get_result = fake_get_result

    client = app.test_client()
    response = await client.get("/result?id=sunarp-task-123")
    data = await response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ready"
    assert data["image"] == "base64-image"
    assert data["placa"] == "ABC123"
