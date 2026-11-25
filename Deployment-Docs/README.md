# VANTAGE360 API — Colab and Local Setup



## 1. Prerequisites and model compatibility

- **Python:**  >=3.11 (Currently using 3.11.9)
- **Dependencies:** prefer versions pinned in the project's requirements files with their own version.
- **Model compatibility:** TensorFlow, PyTorch, scikit-learn, NumPy, and related packages must match the versions used to train or export each saved model.

From the repository root, inspect and install dependencies using the project's actual manifest:

```bash
python --version
uv --version
uv sync --project api --locked
```
Use that `uv sync` command only if `api/pyproject.toml` and `api/uv.lock` exist and are the intended dependency source. If they do not exist, follow the actual requirements/lock file instead.
## 2. Directory and startup command

Run the application from the **repository root**—the directory containing the top-level `api/` directory—so that `api.app.main` can be imported.

Windows PowerShell:

```powershell
uv run python -m uvicorn api.app.main:app --reload
```

Expected local base URL: `http://127.0.0.1:8000`

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## 3. Environment file and secrets

**The exact environment-file path must be verified in `api/app/config.py`.** Do not assume the application automatically loads `.env`. Check the settings loader for its dotenv path and required variable names.

A local `.env` may be stored at the repository root or under `api/`; use only the location the application actually reads. Keep real `.env` files out of Git and use `.env.example` for variable names with placeholder values only.

For Google Colab, supply required values through Colab Secrets or runtime environment variables. Do not upload production credentials to a shared notebook. The exact required variable names must be taken from `api/app/config.py` and the project's configuration.

## 4. Google Colab setup

1. Clone or upload the repository into the Colab runtime.
2. Change directory to the repository root (the directory containing `api/`).
3. Install dependencies using the project's actual manifest and locked versions. If the project uses `uv`, install it in the runtime and follow the lock-file instructions in Section 1.
4. Configure required variables securely using Colab Secrets or environment variables.
5. Start Uvicorn using the command in Section 2.
6. Test health and readiness from the same runtime.

Colab runtimes are temporary, so installed packages and generated files may disappear after a runtime reset. A server running in Colab is not automatically reachable from your local machine; any external tunnel must be explicitly configured and approved. Do not expose sensitive customer data or credentials to the public internet.

## 5. Health, readiness, and documentation

With the API running locally:

```bash
curl -i http://127.0.0.1:8000/api/v2/health
curl -i http://127.0.0.1:8000/api/v2/readiness
curl -i http://127.0.0.1:8000/docs
```

- `GET /api/v2/health` — health/liveness endpoint.
- `GET /api/v2/readiness` — readiness endpoint; verify it confirms that required dependencies and model services are ready.
- `GET /docs` — interactive Swagger UI.
- `GET /openapi.json` — generated API schema.

Confirm expected status codes and response bodies from the running app and automated tests. A successful liveness response alone does not prove every model or downstream service is ready.

## 6. Test customer ID and sample requests

The previously used sample customer ID is **`CUST00001`**.

Previously identified routes:

- `POST /api/v2/churn/predict`
- `POST /api/v2/forecast/predict`
- `POST /api/v2/recommendation/predict`
- `POST /api/v2/customer-intelligence/brief`
- `POST /api/v2/report/generate`


```bash
curl -s http://127.0.0.1:8000/openapi.json
```

Or open `http://127.0.0.1:8000/docs`, select a route, and use its documented request-body schema. If API-key authentication is enabled, use the documented header; the project has previously used `X-API-Key`. Never place a real key in a shared notebook or committed command.

**Sample customer:** `CUST00001`  
**Sample response:** use a response returned by a valid request against the current test environment.
