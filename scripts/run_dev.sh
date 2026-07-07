#!/usr/bin/env bash
set -euo pipefail

python -m turnstile_lab.main \
  --host 127.0.0.1 \
  --port 5072 \
  --debug \
  --browser-type chromium \
  --thread-count 2 \
  --preheat-url https://consultavehicular.sunarp.gob.pe/