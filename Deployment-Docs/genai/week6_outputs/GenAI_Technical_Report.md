# VANTAGE360 — Week 6 GenAI Technical Report
Prepared by Pavithra Veerapathiran

## Scope and architecture
Role-aware Copilot → allowlisted router → approved document retrieval / governed KPI snapshot / versioned API contracts → source evidence → optional constrained LLM report.
Executive and operational roles change presentation. This single-user notebook does not establish production identity or authorization.

## Executed evidence
{
  "week": 6,
  "generated_at": "2026-10-26T14:55:13.119390+00:00",
  "queries_attempted": 40,
  "routing_accuracy": 1.0,
  "answer_quality_review": "PENDING",
  "api_configured": false,
  "docker_compose_validation": "PENDING_EXTERNAL_TEAM",
  "observability_trace_validation": "PENDING_EXTERNAL_TEAM",
  "baseline_v1_v2_v3_regression": "PENDING_IMPORTED_BASELINES",
  "production_signoff": "NOT_ASSERTED"
}

Routing accuracy measures routing only. Service failures, denied access and missing evidence are not successful business answers. Evidence-only rendering is not LLM synthesis. Report generation requires an approved LLM endpoint.

## Evaluation and Responsible AI
See business_evaluation.xlsx, retrieval_comparison when gold labels exist, report_evaluation_15 where applicable, and security/failure/cache tables. Blank human-review fields are pending. Controlled fixtures are labelled test evidence and are not business datasets.

## API integration findings
The supplied ZIP contains source, not a deployed URL. Required model artifacts and governed datasets are separate dependencies. Report API assembles structured inputs; it does not itself provide an LLM narrative. API-level churn cache freshness must be validated by the AI Engineer; notebook cache tests do not certify backend caches.

## Known limitations and remaining actions
- Ask DA for fresh approved KPI snapshots, definitions, dimension/period labels and dashboard/SQL references.
- Ask AI Engineer for reachable base URL/version prefix, approved key, test IDs, model artifact versions and source-refresh guarantees.
- Review at least 40 Week 6 answers / 50 Week 7 answers against independent gold evidence; fill expected answers and reviewer scores.
- Reconcile at least 20 KPI questions with dashboard/SQL in Week 6.
- Import actual versioned baseline outputs before claiming comparative regression.
- Review all red-team failures, record fixes, and rerun after changes.
- Validate Docker integration, model parity, observability and production authorization with the team outside Colab.
- Model tuning, SHAP and model cards mentioned in the Week 4 shared predictive track require real training data and model artifacts; this GenAI notebook does not claim them complete.
