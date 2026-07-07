# Adapters

Adapters implement site-specific browser workflows. Unlike generic solvers, adapters know the target page structure, selectors, submission flow, and result extraction rules.

## Contract

An adapter receives a reusable `BrowserSession` and a payload dictionary with the input fields required by the target site.

Adapters return normalized dictionaries:

```json
{"status": "ready"}
```

or:

```json
{"status": "error", "error": "message"}
```

The task manager stores that result without the API needing to know the page internals.

## SUNARP

The SUNARP adapter automates vehicle plate consultation:

1. Fill `input#nroPlaca`.
2. Click a submit button.
3. Wait for one of the known result containers.
4. Extract an inline image or screenshot the result container.
5. Return `{"status": "ready", "placa": "...", "image": "base64..."}`.

### Main selectors

- Plate input: `input#nroPlaca`.
- Submit button candidates: `button.ant-btn-primary`, `button[type="submit"]`, `input[type="submit"]`.
- Success containers: `.container-data-vehiculo`, `.ant-table`, `.resultado-consulta`, `.vehiculo-info`.
- Image candidates: images inside result containers.

When selectors change, update only `adapters/sunarp/selectors.py` or the adapter implementation.
