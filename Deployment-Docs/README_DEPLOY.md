# Vantage360 dashboard deployment starter

## What is included
- Original Streamlit `dashboard/executive_app.py` and `dashboard/app.py` from Pappu's Week 8 archive; not rewritten.
- Required supporting `src/data_analysis`, `data/processed`, and executive report snapshot from that archive.
- New deployment configuration (`requirements.txt`, `Dockerfile`, `.streamlit/config.toml`) and a static validation script.

This is a **historical analytics demo**, not an approved production release. The executive snapshot is for December 2024 and the manifest states `ai_approval: Pending joint review` and `threshold_approval: Provisional analyst rules`. Predictive conclusions are not approved.

## Local Windows setup
Open PowerShell in the extracted `Vantage360_Deployment_Starter` folder and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python CHECK_DEPLOYMENT.py
python -m streamlit run dashboard/executive_app.py
```

Visit `http://localhost:8501`. For retention cockpit: `python -m streamlit run dashboard/app.py`.

## Deploy on Streamlit Community Cloud (only with owner approval)
1. Create a **private** GitHub repository (or approved protected branch) for this starter directory and upload its contents to the repository root. Do not upload secrets or confidential customer data without formal authorization.
2. In https://share.streamlit.io choose **Create app** / **Deploy an app**, authorize your GitHub repository, and select branch and entrypoint `dashboard/executive_app.py`.
3. Deploy and check the app logs and displayed KPI values. Grant viewer access only to authorized stakeholders.
4. If you don't have repository permissions, ask the repo owner to authorize deployment or perform it.

## Deploy with Render Docker (only with owner approval)
Create a Render Web Service linked to your approved repository, select Docker runtime with `Dockerfile` in the repository root, and deploy. The Dockerfile starts Streamlit listening on port 8501. Check Render logs and service URL. Set access protection before exposing any nonpublic data.

## Validation
`python CHECK_DEPLOYMENT.py` checks path existence, Python syntax, and saved manifest metadata. It **does not** validate installed dependency compatibility, visual rendering, authorization, or live hosting. The app must be run and reviewed by a human.

## API and GenAI components not included in this runnable dashboard
The uploaded Fadoua API archive contains FastAPI source, but the full backend isn't verified ready: `customer_features.csv` is absent from uploaded sources; Fadoua's original Dockerfile tries `COPY VANTAGE_Datasets` although only a `VANTAGE_Datasets.zip` archive exists at root; some additional model artifacts are in the historical full-source ZIP. The Week 8 Copilot evidence also has unresolved G06/G07/G13 guardrail failures and policy corpus dependencies. Do not treat this dashboard deployment as a complete Vantage360 integration.

## Security and release notes
- Dashboard package includes historical processed snapshot files. Review for personal/customer data before pushing or hosting. Use a **private** repository and restricted app by default.
- Avoid uploading `.env`, API keys, private notebooks or source ZIPs with credentials.
- Before production hosting: gain data owner authorization, close UAT/security issues, run functionality and integration tests, approve model/data provenance, configure logging and observability.
