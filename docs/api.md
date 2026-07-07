# API

Base URL:

```text
http://127.0.0.1:5072
```

## GET /

Returns a basic service description and route hints.

```json
{
  "name": "turnstile-browser-lab",
  "status": "ok",
  "docs": {
    "turnstile": "/turnstile?url=...&sitekey=...",
    "consultar": "/consultar?url=...&sitekey=...&placa=ABC123",
    "result": "/result?id=task_id",
    "health": "/health"
  }
}
```

## GET /health

Returns a lightweight health check with runtime configuration.

```json
{
  "status": "ok",
  "browser_type": "chromium",
  "thread_count": 4,
  "headless": true
}
```

## GET /turnstile

Creates a Turnstile solving task.

Query parameters:

- `url`: required target page URL.
- `sitekey`: required Turnstile site key.
- `action`: optional action value.
- `cdata`: optional custom data value.

Success:

```json
{
  "errorId": 0,
  "taskId": "task-id-here"
}
```

Validation error:

```json
{
  "errorId": 1,
  "errorCode": "ERROR_WRONG_PAGEURL",
  "errorDescription": "Both 'url' and 'sitekey' are required"
}
```

## GET /consultar

Creates a SUNARP vehicle lookup task.

Query parameters:

- `url`: required SUNARP page URL.
- `sitekey`: required for compatibility with the original endpoint.
- `placa`: required vehicle plate, normalized before task creation.

Success:

```json
{
  "errorId": 0,
  "taskId": "task-id-here"
}
```

Validation error:

```json
{
  "errorId": 1,
  "errorCode": "ERROR_WRONG_PARAMETERS",
  "errorDescription": "'url', 'sitekey' and 'placa' are required"
}
```

## GET /result

Polls the current state of a task.

Query parameters:

- `id`: required task identifier.

Processing:

```json
{
  "status": "processing"
}
```

Ready Turnstile:

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "token": "token-value"
  }
}
```

Turnstile error:

```json
{
  "errorId": 1,
  "errorCode": "ERROR_CAPTCHA_UNSOLVABLE",
  "errorDescription": "Could not solve the Captcha"
}
```

Ready SUNARP:

```json
{
  "status": "ready",
  "image": "base64-image-data",
  "placa": "ABC123"
}
```

SUNARP error:

```json
{
  "status": "error",
  "error": "No se encontraron resultados para ABC123"
}
```
