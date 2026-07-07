# Architecture

Turnstile Browser Lab is an async browser automation service. It exposes HTTP endpoints, manages a reusable browser pool, runs work in background tasks, and stores results for polling clients.

## Components

- `api/`: Quart application, request validation, and response shaping.
- `core/`: Browser pool, task manager, shared models, and cache.
- `solvers/`: Generic challenge solvers such as Turnstile.
- `adapters/`: Site-specific automation flows such as SUNARP plate lookup.
- `profiles/`: Browser identity selection with `User-Agent` and `sec-ch-ua` values.
- `storage/`: Result persistence, currently SQLite via `aiosqlite`.
- `utils/`: Validation, timers, hashes, and cache-key helpers.

## Request flow

1. A client calls `/turnstile` or `/consultar`.
2. The API validates query parameters and creates a task identifier.
3. The initial task state is stored as pending.
4. A background task acquires a browser session from the pool.
5. A solver or adapter runs the browser workflow.
6. The normalized result is stored in SQLite.
7. The client polls `/result?id=...` until the task is ready or failed.

## Browser sessions

The browser pool launches a fixed number of sessions on startup. Requests borrow a session, run a solver or adapter, and release the session back to the queue.

`browser_type="chromium"` launches bundled Chromium without a channel. `chrome` and `msedge` are passed as Playwright channels.

## Persistence

Results are stored in SQLite using WAL mode and other pragmas intended to improve concurrent access. Old records are removed periodically according to `result_ttl_days`.

## Caching

SUNARP lookups cache task IDs with a key built from the normalized plate plus `md5(url)`. This keeps repeated plate lookups fast while still using the same `/result` polling contract.
