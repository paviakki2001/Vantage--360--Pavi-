# Copilot Operations Guide

Owner: Pavithra Veerapathiran | Run: 20261115T030457018121Z

## Start
Use a fresh Colab CPU runtime. Run sections 1–10 in order, upload the complete project ZIP, and optionally place the bridge ZIP in /content. The notebook sets isolated runtime settings and generates an ephemeral API key without exporting it.

## Operate
Use copilot(question, role="executive" or "operational", session="demo"). Supported routes: KPI analytics, churn, recommendation, forecast and cited extractive business retrieval. Customer requests need a valid CUST identifier.

## Troubleshoot
Missing source: confirm the complete source ZIP. Version mismatch: restart and use the model owner-compatible environment; never hide serialization warnings. NEED_CUSTOMER_ID: provide a valid ID. NO_FEATURE_ROW: do not invent scores. ABSTAIN: inspect available evidence. API failure: inspect api_validation.csv. Source changes: rerun data/model/retrieval cells and evaluation; do not reuse stale in-memory outputs.

## Incident and recovery
Stop the demo on unexpected disclosure or incorrect financial/customer output. Record test ID and minimal evidence, notify technical owner through the normal team channel, correct, rerun regressions and obtain review. Restore a known approved source package and matching environment for rollback.

Lexical TF-IDF/BM25 fusion with source-derived labels; no dense semantic retriever, learned reranker or LLM narrative. Role/session inputs are local fixtures. HTTP checks are in-process. Customer support issues are not approved resolution policy. Forecast dates are retained from supplied artifacts. Policy corpus is unavailable. No hosted accessibility or production certification is asserted.
