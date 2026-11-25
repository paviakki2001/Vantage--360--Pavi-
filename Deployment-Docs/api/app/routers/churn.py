from fastapi import APIRouter, Depends, Request

from api.app.services.churn_service import ChurnService
from api.app.data_access.Controlled_file import DatasetRepository
from api.app.errors import AppException

from api.app.config import settings
from functools import lru_cache
from orchestration.workflows.ai_workflow import AIWorkflow
from datetime import datetime, timezone
from api.app.schemas.model_api import (
    CustomerModelRequest,
    StandardModelResponse,
)
import logging
from api.app.gateway.authentication import (
    require_api_key,
)
from api.app.observability.metrics import metrics

logger = logging.getLogger("vantage360-ai")


router = APIRouter(
    prefix="/churn",
    tags=["Churn"],
    dependencies=[
        Depends(require_api_key)
    ],
)

@lru_cache
def get_churn_service() -> ChurnService:
    repository = DatasetRepository(settings.master_data_directory)
    return ChurnService(repository)

@router.post("/predict", response_model=StandardModelResponse,)
def predict_churn(
        request: CustomerModelRequest,
        churn_service: ChurnService = Depends(get_churn_service),
):
    customer_id = request.customer_id.strip().upper()

    logger.info(
        "Churn prediction request received "
        "customer_id=%s",
        customer_id,
    )
    try:
        result = churn_service.predict(customer_id)
        timestamp = (datetime.now(timezone.utc).isoformat())

        logger.info(
            "Churn prediction completed "
            "customer_id=%s model_version=%s",
            customer_id,
            result.get("model_version"),
        )


        return {
                "tool": "churn_risk",
                "version": "v2",
                "input": {
                    "customer_id": customer_id.strip().upper(),
                },
                "output": result,
                "status": "success",
                "timestamp": timestamp,
                "metadata": {
                        "model_version": result.get(
                         "model_version"
                         ),}
            }

    except ValueError as exc:

        logger.warning(
            "Churn validation failure "
            "customer_id=%s error=%s",
            customer_id,
            exc,
        )

        raise AppException(
            message=str(exc),
            status_code=400,
        ) from exc

    except TimeoutError as exc:

        logger.error(
            "Churn prediction timeout "
            "customer_id=%s",
            customer_id,
        )

        raise AppException(
            message="Churn prediction timed out.",
            status_code=504,
        ) from exc

    except Exception as exc:

        metrics.record_model_failure(
            "churn"
        )

        logger.exception(
            "Churn prediction failed "
            "customer_id=%s",
            customer_id,
        )

        raise AppException(
            message="Churn prediction failed.",
            status_code=500,
        ) from exc

@router.post("/query")
def churn_query(
        question: str,
        request: Request,
        churn_service: ChurnService = Depends(get_churn_service),
):
    correlation_id = request.state.correlation_id

    if not question or not question.strip():
        raise AppException(
            message="question is required.",
            status_code=400,
        )

    workflow = AIWorkflow(churn_service)

    correlation_id = request.state.correlation_id


    try:
        return workflow.process_question(
            question,
            correlation_id=correlation_id,
        )


    except ValueError as exc:
        raise AppException(
            message=str(exc),
            status_code=400,
        ) from exc