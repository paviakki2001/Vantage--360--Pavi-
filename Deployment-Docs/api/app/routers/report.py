from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends

from api.app.errors import AppException
from api.app.services.report_generation_service import (
    ReportGenerationService,
)
from orchestration.workflows.report_generation_workflow import (
    ReportGenerationWorkflow,
)
from api.app.gateway.authentication import (
    require_api_key,
)

router = APIRouter(
    prefix="/report",
    tags=["Report Generation"],
    dependencies=[
        Depends(require_api_key)
    ],
)


@lru_cache
def get_report_generation_service() -> ReportGenerationService:
    return ReportGenerationService()


@router.post("/generate")
def generate_report(
        model_outputs: dict[str, Any],
        kpi_snapshot: dict[str, Any],
        business_context: dict[str, Any],
        report_service: ReportGenerationService = Depends(
            get_report_generation_service
        ),
):
    workflow = ReportGenerationWorkflow(
        report_service
    )

    try:
        result = workflow.run(
            model_outputs=model_outputs,
            kpi_snapshot=kpi_snapshot,
            business_context=business_context,
        )

        return {
            "tool": "customer_intelligence_report",
            "version": "v1",
            "input": {
                "model_outputs": model_outputs,
                "kpi_snapshot": kpi_snapshot,
                "business_context": business_context,
            },
            "output": result,
            "status": "success",
        }

    except ValueError as exc:
        raise AppException(
            message=str(exc),
            status_code=400,
        ) from exc