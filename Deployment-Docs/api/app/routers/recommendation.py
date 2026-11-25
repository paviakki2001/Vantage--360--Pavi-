from functools import lru_cache

from fastapi import APIRouter, Depends

from api.app.errors import AppException
from api.app.services.recommendation_service import (
    RecommendationService,
)
from datetime import datetime, timezone
import logging
from api.app.schemas.model_api import (
    CustomerModelRequest,
    StandardModelResponse,
)
from api.app.errors import AppException
from api.app.gateway.authentication import (
    require_api_key,
)
from api.app.observability.metrics import metrics


logger = logging.getLogger("vantage360-ai")

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"],
    dependencies=[
        Depends(require_api_key)
    ],
)


@lru_cache
def get_recommendation_service() -> RecommendationService:
    return RecommendationService()


@router.post("/predict", response_model=StandardModelResponse,)
def predict_recommendation(
        request: CustomerModelRequest,
        recommendation_service: RecommendationService = Depends(
            get_recommendation_service
        ),
):
    customer_id = request.customer_id.strip().upper()

    logger.info(
        "Recommendation request received "
        "customer_id=%s",
        customer_id,
    )

    try:

        result = (
            recommendation_service.get_recommendation(
                customer_id
            )
        )

        timestamp = (
            datetime.now(timezone.utc).isoformat()
        )

        logger.info(
            "Recommendation completed "
            "customer_id=%s",
            customer_id,
        )

        return {
            "tool": "next_best_action",
            "version": "v1",
            "input": {
                "customer_id": customer_id,
            },
            "output": result,
            "metadata": {
                "model_version": result.get(
                    "model_version"
                ),
                "engine_type": "rule_based",
            },
            "status": "success",
            "timestamp": timestamp,
        }

    except ValueError as exc:

        logger.warning(
            "Recommendation validation failure "
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
            "Recommendation timeout "
            "customer_id=%s",
            customer_id,
        )

        raise AppException(
            message="Recommendation timed out.",
            status_code=504,
        ) from exc

    except Exception as exc:
        metrics.record_model_failure(
            "recommendation"
        )

        logger.exception(
            "Recommendation failed "
            "customer_id=%s",
            customer_id,
        )

        raise AppException(
            message="Recommendation service failed.",
            status_code=500,
        ) from exc
