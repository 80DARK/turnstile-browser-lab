import pytest

from turnstile_lab.core.task_manager import TaskManager


class DummyLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass


class DummySession:
    index = 1


class DummyBrowserPool:
    def __init__(self):
        self.session = DummySession()
        self.acquired = 0
        self.released = 0

    async def acquire(self):
        self.acquired += 1
        return self.session

    async def release(self, session):
        self.released += 1


class DummySolver:
    async def solve(self, session, payload):
        return {
            "status": "ready",
            "value": "mock-token",
            "elapsed_time": 0.123,
        }


class DummySunarpAdapter:
    async def run(self, session, payload):
        return {
            "status": "ready",
            "image": "base64-image",
            "placa": payload["placa"],
        }


@pytest.mark.asyncio
async def test_create_turnstile_task_saves_initial_state(monkeypatch):
    saved = {}

    async def fake_save_result(task_id, task_type, data):
        saved[task_id] = {"type": task_type, "data": data}

    async def fake_init_db():
        return None

    pool = DummyBrowserPool()
    manager = TaskManager(browser_pool=pool, logger=DummyLogger())
    manager.turnstile_solver = DummySolver()

    monkeypatch.setattr("turnstile_lab.core.task_manager.save_result", fake_save_result)
    monkeypatch.setattr("turnstile_lab.core.task_manager.init_db", fake_init_db)

    await manager.startup()
    task_id = await manager.create_turnstile_task(
        url="https://example.com",
        sitekey="sitekey-123",
    )

    assert task_id in saved
    assert saved[task_id]["type"] == "turnstile"
    assert saved[task_id]["data"]["status"] == "CAPTCHA_NOT_READY"
    assert saved[task_id]["data"]["url"] == "https://example.com"
    assert saved[task_id]["data"]["sitekey"] == "sitekey-123"
    
@pytest.mark.asyncio
async def test_run_turnstile_task_saves_solver_result(monkeypatch):
    saved_calls = []

    async def fake_save_result(task_id, task_type, data):
        saved_calls.append((task_id, task_type, data))

    pool = DummyBrowserPool()
    manager = TaskManager(browser_pool=pool, logger=DummyLogger())
    manager.turnstile_solver = DummySolver()

    monkeypatch.setattr("turnstile_lab.core.task_manager.save_result", fake_save_result)

    await manager._run_turnstile_task(
        task_id="task-123",
        url="https://example.com",
        sitekey="sitekey-123",
    )

    assert pool.acquired == 1
    assert pool.released == 1
    assert saved_calls[-1][0] == "task-123"
    assert saved_calls[-1][1] == "turnstile"
    assert saved_calls[-1][2]["status"] == "ready"
    assert saved_calls[-1][2]["value"] == "mock-token"


@pytest.mark.asyncio
async def test_create_sunarp_task_uses_cache(monkeypatch):
    saved = {}

    async def fake_save_result(task_id, task_type, data):
        saved[task_id] = {"type": task_type, "data": data}

    pool = DummyBrowserPool()
    manager = TaskManager(browser_pool=pool, logger=DummyLogger())
    manager.sunarp_adapter = DummySunarpAdapter()

    monkeypatch.setattr("turnstile_lab.core.task_manager.save_result", fake_save_result)

    first_task_id = await manager.create_sunarp_task(
        url="https://consultavehicular.sunarp.gob.pe/",
        placa="ABC123",
    )
    second_task_id = await manager.create_sunarp_task(
        url="https://consultavehicular.sunarp.gob.pe/",
        placa="ABC123",
    )

    assert second_task_id == first_task_id
    assert first_task_id in saved
    assert saved[first_task_id]["type"] == "consulta"
    assert saved[first_task_id]["data"]["status"] == "PROCESSING"


@pytest.mark.asyncio
async def test_run_sunarp_task_saves_adapter_result(monkeypatch):
    saved_calls = []

    async def fake_save_result(task_id, task_type, data):
        saved_calls.append((task_id, task_type, data))

    pool = DummyBrowserPool()
    manager = TaskManager(browser_pool=pool, logger=DummyLogger())
    manager.sunarp_adapter = DummySunarpAdapter()

    monkeypatch.setattr("turnstile_lab.core.task_manager.save_result", fake_save_result)

    await manager._run_sunarp_task(
        task_id="sunarp-task-123",
        url="https://consultavehicular.sunarp.gob.pe/",
        placa="ABC123",
    )

    assert pool.acquired == 1
    assert pool.released == 1
    assert saved_calls[-1][0] == "sunarp-task-123"
    assert saved_calls[-1][1] == "consulta"
    assert saved_calls[-1][2]["status"] == "ready"
    assert saved_calls[-1][2]["image"] == "base64-image"
