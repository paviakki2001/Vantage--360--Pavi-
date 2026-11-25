from functools import lru_cache

from fastapi import APIRouter, Depends, Header

from api.app.config import settings
from api.app.data_access.Controlled_file import DatasetRepository
from api.app.errors import AppException
from api.app.services.customer_intelligence_service import (
    CustomerIntelligenceService,
)
from orchestration.workflows.customer_intelligence_workflow import (
    CustomerIntelligenceWorkflow,
)
from uuid import uuid4
from api.app.gateway.authentication import (
    require_api_key,
)

router = APIRouter(
    prefix="/customer-intelligence",
    tags=["Customer Intelligence"],
    dependencies=[
        Depends(require_api_key)
    ],
)


@lru_cache
def get_customer_intelligence_service() -> CustomerIntelligenceService:
    repository = DatasetRepository(
        settings.master_data_directory
    )

    return CustomerIntelligenceService(repository)


@router.post("/brief")
def customer_intelligence_brief(
        customer_id: str,
        correlation_id: str | None = Header(
            default=None,
            alias="X-Correlation-ID",),
        intelligence_service: CustomerIntelligenceService = Depends(
            get_customer_intelligence_service
        ),
):
    if not customer_id or not customer_id.strip():
        raise AppException(
            message="customer_id is required.",
            status_code=400,
        )

    workflow = CustomerIntelligenceWorkflow(
        intelligence_service
    )

    try:
        result = workflow.run(customer_id)

        return {
            "tool": "customer_intelligence_brief",
            "version": "v1",
            "input": {
                "customer_id": customer_id.strip().upper(),
            },
            "output": result,
            "status": "success",
        }

    except ValueError as exc:
        raise AppException(
            message=str(exc),
            status_code=400,
        ) from exc