# Turnstile Browser Lab

Async browser automation service for Turnstile solving and site-specific adapters such as SUNARP.

The project exposes a small HTTP API, reuses browser sessions through a pool, runs work in background tasks, and stores results in SQLite so clients can poll until a task is ready.

## Features

- Turnstile task creation and polling.
- Reusable browser session pool.
- Browser identity profiles with `User-Agent` and `sec-ch-ua`.
- SQLite-backed result storage.
- SUNARP vehicle lookup adapter with cached task IDs.
- Tests, examples, scripts, and docs split away from the app code.

## Project structure

- `src/turnstile_lab/api/` - Quart app and routes.
- `src/turnstile_lab/core/` - Browser pool, task manager, models, cache.
- `src/turnstile_lab/solvers/` - Generic solving logic.
- `src/turnstile_lab/adapters/` - Site-specific flows.
- `src/turnstile_lab/profiles/` - Browser identity configuration.
- `src/turnstile_lab/storage/` - Persistence layer.
- `src/turnstile_lab/utils/` - Shared helpers.
- `tests/` - Unit/API tests for the refactor.
- `docs/` - Architecture, adapter, and API documentation.
- `examples/` - Example clients and `.http` requests.
- `scripts/` - Dev and benchmark utilities.

## Installation

```bash
pip install -e .[dev]
```

Or install only runtime dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m turnstile_lab.main --debug --browser-type chromium --thread-count 2
```

On Windows you can also use:

```bat
scripts\run_dev.bat
```

## Endpoints

- `GET /`
- `GET /health`
- `GET /turnstile?url=...&sitekey=...`
- `GET /consultar?url=...&sitekey=...&placa=ABC123`
- `GET /result?id=...`

## Example Turnstile flow

Create a task:

```text
GET /turnstile?url=https://example.com&sitekey=YOUR_SITEKEY
```

Poll the result:

```text
GET /result?id=TASK_ID
```

Possible responses:

```json
{"status": "processing"}
```

```json
{"errorId": 0, "status": "ready", "solution": {"token": "..."}}
```

```json
{"errorId": 1, "errorCode": "ERROR_CAPTCHA_UNSOLVABLE", "errorDescription": "Could not solve the Captcha"}
```

## Example SUNARP flow

```text
GET /consultar?url=https://consultavehicular.sunarp.gob.pe/&sitekey=SITEKEY&placa=ABC123
```

Then poll `/result?id=TASK_ID`.

Ready SUNARP responses include the normalized plate and a base64 image:

```json
{"status": "ready", "image": "...", "placa": "ABC123"}
```

## Development

```bash
pytest
```

This project depends on browser automation tooling and live target pages. Selectors can change, so site adapters are intentionally isolated from the API and storage layers.
