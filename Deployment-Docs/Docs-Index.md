
# Vantage360 — Documentation Index

## Project Overview

Vantage360 is a customer intelligence platform integrating
business analytics, machine learning, FastAPI services,
Streamlit dashboards, and GenAI Copilot components.

**Current Status:** Integration and deployment candidate.
Production readiness and full GenAI integration are pending.

---

## 1. Main Project Documentation

| Document | Description |
|---|---|
| [Full Platform README](README_FULL_PLATFORM.md) | Project structure, integration scope, limitations, and outstanding tasks |
| [Deployment README](README_DEPLOY.md) | Dashboard setup, local execution, and hosting options |
| [Render Connection Instructions](RENDER_CONNECT_INSTRUCTIONS.md) | FastAPI and Streamlit deployment configuration, connection settings, and test flows |

## 2. FastAPI Backend Documentation

| Document | Description |
|---|---|
| [API Setup Guide](api/README.md) | API environment setup, model compatibility, local and Colab execution |
| [Release Readiness Checklist](api/reports/VANTAGE360_Release_Readiness_Evidence_Checklist.md) | Performance, observability, infrastructure, rollback, and readiness requirements |
| [Infrastructure and Release Readiness Report](api/reports/VANTAGE360_Infrastructure_Optimization_and_Release_Readiness_Report.md) | Infrastructure performance, optimization, and deployment-readiness evidence |
| [Release and Recovery Runbook](api/reports/VANTAGE360_Release_Recovery_and_Monitoring_Runbook.md) | Deployment, health monitoring, rollback, and incident recovery |
| [Integrated Test Pack](api/tests/release_readiness/README.md) | Release-readiness test execution and reporting |

## 3. Analytics and Dashboard Documentation

| Document | Description |
|---|---|
| [Executive Analytics Report](reports/week5_da11_executive_analytics_report.md) | Revenue, customers, marketing, service performance, and predictive business insights |

## 4. GenAI Copilot Documentation

| Document | Description |
|---|---|
| [GenAI Technical Report](genai_evidence/documentation/GenAI_Technical_Report_Week8.md) | Week 8 architecture, execution evidence, limitations, and handover |
| [RAG Evaluation Report](genai_evidence/documentation/RAG_Evaluation_Report_Week8.md) | Retrieval evaluation, test coverage, and review findings |
| [Red-Team and Guardrail Report](genai_evidence/documentation/Red_Team_and_Guardrail_Report.md) | Security validation, guardrails, open defects, and limitations |
| [Copilot Operations Guide](genai_evidence/documentation/Copilot_Operations_Guide.md) | Copilot operations, troubleshooting, and incident handling |
| [Knowledge Base Refresh Procedure](genai_evidence/documentation/Knowledge_Base_Refresh_Procedure.md) | Knowledge-base maintenance and refresh instructions |
| [Operational Quick-Start](genai_evidence/documentation/Operational_Quick_Start.md) | Operational instructions for Copilot users |
| [Executive Quick-Start](genai_evidence/documentation/Executive_Quick_Start.md) | Executive-facing Copilot usage instructions |
| [Deployment and Handover Plan](genai_evidence/documentation/Deployment_Preparation_and_Handover_Plan.md) | Deployment requirements, acceptance gates, and team handover |
| [Week 8 Submission Index](genai_evidence/documentation/README_Week8_Submission.md) | GenAI deliverables and submission details |

---

## 5. Recommended Reading Order

1. Full Platform README
2. Render Connection Instructions
3. API Setup Guide
4. Release Readiness Checklist
5. Infrastructure and Release Readiness Report
6. GenAI Technical Report
7. RAG Evaluation Report
8. Red-Team and Guardrail Report
9. Deployment and Handover Plan
10. Release and Recovery Runbook

---

## 6. Deployment Readiness Notes

Before declaring the complete platform deployed:

- Verify the FastAPI service starts successfully.
- Confirm required datasets and ML models load.
- Test churn, forecasting, and recommendation endpoints.
- Verify Streamlit-to-FastAPI connectivity.
- Integrate and test the runnable GenAI Copilot service.
- Resolve outstanding GenAI guardrail failures.
- Complete integration, security, and user acceptance testing.
- Verify monitoring and recovery procedures.

**Note:** The presence of documentation does not establish
that the corresponding component has passed live testing.

---

## 7. Technology Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Machine Learning:** Python, scikit-learn
- **GenAI:** LLM, RAG, retrieval, and guardrail components
- **Data:** CSV and Parquet
- **Version Control:** GitHub
- **Target Hosting:** Render

---

*Vantage360 Customer Intelligence Platform*
*Documentation Index — Week 8 Integration and Deployment*
