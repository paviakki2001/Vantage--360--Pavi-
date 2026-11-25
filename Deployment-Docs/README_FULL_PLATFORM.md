# Vantage360 — integration candidate (NOT a production release)

## What this contains
- Fadoua's FastAPI backend and orchestration sources (`api/`, `orchestration/`).
- Iqra's churn and forecast model artifacts (`models/`) and `customer_features.csv`.
- Pappu's Week 8 executive Streamlit dashboard with historical KPI snapshots (`dashboard/`, `data/`, `src/`).
- Week 8 GenAI notebook and reviewer evidence (`genai_week8_notebook.ipynb`, `genai_evidence/`).

## Critical limitation
**This does not yet implement a hosted LLM/RAG Copilot.** The uploaded GenAI notebook and evidence do not constitute a tested, runnable Copilot API. Do not represent this as a complete live GenAI deployment. The API also needs integration and model compatibility testing before public access.

## Local integration smoke test
1. Install Docker Desktop and Docker Compose.
2. Copy `.env.example` to `.env`, set a strong `GATEWAY_API_KEY`.
3. Run `docker compose up --build` from the folder containing this README.
4. Visit http://localhost:8501 for the executive dashboard. The dashboard displays historical published snapshots; it is not yet connected to live API predictions.
5. Test http://localhost:8000/api/v2/health and `/api/v2/readiness`. Readiness must report all checks as `ready` before claiming complete API integration.
6. Test the authenticated ML predictions using the payloads in `api/README.md` and the configured API key.
7. Do not deploy publicly until the GenAI Copilot endpoint, policy corpus, guardrails, user review, and integration QA are implemented and verified.

## Outstanding work
- Confirm supported model serialization versions: source API requirements pin scikit-learn 1.9.1; the checkpoint may require another release. Verify against Iqra's model metadata.
- Confirm all required dataset inputs and schema compatibility; the package contains `customer_features.csv` and five synthetic source CSVs; validate schemas against services.
- Inspect feature/forecast/recommendation service expected artifact names and paths; the two team ZIPs use slightly different conventions.
- Add a runnable GenAI Copilot service (LLM provider configuration, embeddings, vector index, approved policy corpus, citations, authentication, red-team tests).
- Fix GenAI Week 8 guardrail failures G06, G07, G13 and complete stakeholder review.
- Secure authentication, secrets, rate-limiting and restrict public access appropriately.

This ZIP is intended for a **private test branch / local Docker integration** first. Do not upload unchanged as a production-ready project.
