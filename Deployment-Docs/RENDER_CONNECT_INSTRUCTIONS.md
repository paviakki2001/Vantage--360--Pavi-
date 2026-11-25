# Vantage360 Render connection — candidate, not final deployment

## What changed
- Added `dashboard/pages/1_Live_ML_Predictions.py` as an extra page beside the existing Streamlit executive dashboard.
- Added `requests` to the **root** `requirements.txt`.
- Original API routes and original dashboards were not modified.
- GenAI Copilot remains **not implemented as a deployable API**.

## 1. API Render web service
Use the repository root as the Render root directory (leave blank), native Python, Build Command `pip install -r api/requirements.txt`, and Start Command `uvicorn api.app.main:app --host 0.0.0.0 --port $PORT`.

The FastAPI `Settings` class requires environment variables. Configure these in Render under **API service -> Environment**, adjusting to your deployment:
```
APP_NAME=Vantage360 API
SERVICE_NAME=vantage360-api
ENVIRONMENT=development
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1
API_V2_PREFIX=/api/v2
DATA_SOURCE_MODE=development_csv
MASTER_DATA_DIRECTORY=/opt/render/project/src/VANTAGE_Datasets/datasets
SERVICE_BASE_URL=https://YOUR-API-HOST.onrender.com
SERVICE_TIMEOUT_SECONDS=30
GATEWAY_AUTH_ENABLED=true
GATEWAY_API_KEY=<SET-A-STRONG-UNIQUE-SECRET-IN-RENDER-ONLY>
```
`MASTER_DATA_DIRECTORY` assumes Render uses `/opt/render/project/src` for the root; verify the path if the structure changes. Do **not** store the real key in GitHub. `GATEWAY_RATE_LIMIT` and `GATEWAY_RATE_WINDOW_SECONDS` have defaults.

Test `/api/v2/health`, `/api/v2/readiness`, and the secured POST routes. The API's pinned dependencies / serialized ML artifacts still require compatibility testing, so initial build or readiness may fail. Fix before advertising it as operational.

## 2. Dashboard Render web service
Use same repository / root, native Python, Build Command `pip install -r requirements.txt`, and Start Command:
```
streamlit run dashboard/executive_app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
```
Set these environment variables on **dashboard service -> Environment**:
```
VANTAGE_API_URL=https://YOUR-ACTUAL-API-HOST.onrender.com
VANTAGE_API_KEY=<THE-SAME-SECRET-AS-API-SERVICE-GATEWAY_API_KEY>
```
Deploy and find the `Live ML Predictions` page in the Streamlit sidebar. The request is server-side, so the API key is not embedded in the repository. Still require application/user authentication if exposing private functions publicly; a shared gateway key is **not** sufficient per-user authorization.

## 3. Test flows
- On dashboard page: API health + model readiness; check every model is ready.
- Synthetic customer ID -> Churn prediction; then recommendation.
- Forecast button -> forecast JSON.
- Errors should be investigated in Render API logs, not suppressed or replaced with fake responses.
- Historical KPI dashboard is still snapshot based; it has NOT been changed into live dashboard data.

## 4. GenAI Copilot remains pending
Build a real protected `POST /api/v2/copilot/chat` endpoint after obtaining corpus and LLM credentials, integrating retrieval and session isolation, generating evidence-grounded answers, and passing Week 8 G06/G07/G13 regression tests. The current package does not have that endpoint; do not claim chat is live.

## Deployment caveats
- This is a connectivity patch, **not** a fully tested production build or a full-platform release.
- Reconfirm permission to publish any contributed code; synthetic data does not by itself grant license or sharing rights.
- Do not commit `.env`, API tokens, or platform secrets.
