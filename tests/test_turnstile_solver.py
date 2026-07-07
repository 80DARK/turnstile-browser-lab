import pytest

from turnstile_lab.solvers.turnstile_solver import TurnstileSolver


class DummyLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass


class DummyPage:
    async def evaluate(self, script):
        return "0.token-from-textarea"


class DummySession:
    index = 1
    page = DummyPage()


@pytest.mark.asyncio
async def test_extract_token_reads_turnstile_textarea_value():
    solver = TurnstileSolver(DummyLogger())

    token = await solver._extract_token(DummySession())

    assert token == "0.token-from-textarea"
