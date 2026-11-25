import logging

from fastapi import APIRouter

from api.app.config import settings
from api.app.data_access.Controlled_file import (
    DatasetRepository,
)
from api.app.services.churn_service import ChurnService
from api.app.services.forecast_service import (
    ForecastService,
)
from api.app.services.recommendation_service import (
    RecommendationService,
)
from api.app.observability.metrics import metrics

logger = logging.getLogger("vantage360-ai")


router = APIRouter(
    prefix="/readiness",
    tags=["System"],
)


@router.get("")
def readiness():

    checks = {}

    try:

        repository = DatasetRepository(
            settings.master_data_directory
        )

        churn_service = ChurnService(
            repository
        )

        metrics.set_service_health(
            "churn",
            "ready",
        )

        checks["churn"] = {
            "status": "ready",
            "model_version": (churn_service.MODEL_VERSION),
        }

    except Exception as exc:
        logger.exception(
            "Churn readiness check failed"
        )

        metrics.set_service_health(
            "churn",
            "not_ready",
        )

        checks["churn"] = {
            "status": "not_ready",
            "error": str(exc),
        }

    try:
        forecast_service = ForecastService()

        metrics.set_service_health(
            "forecast",
            "ready",
        )

        checks["forecast"] = {
            "status": "ready",
            "model_version": (
                forecast_service.metadata.get(
                    "model_version"
                )
            ),
        }

    except Exception as exc:
        logger.exception(
            "Forecast readiness check failed"
        )

        metrics.set_service_health(
            "forecast",
            "not_ready",
        )

        checks["forecast"] = {
            "status": "not_ready",
            "error": str(exc),
        }

    try:
        recommendation_service = (
            RecommendationService()
        )

        metrics.set_service_health(
            "recommendation",
            "ready",
        )

        checks["recommendation"] = {
            "status": "ready",
            "model_version": (
                recommendation_service.TOOL_VERSION
            ),
        }

    except Exception as exc:
        logger.exception(
            "Recommendation readiness check failed"
        )

        metrics.set_service_health(
            "recommendation",
            "not_ready",
        )

        checks["recommendation"] = {
            "status": "not_ready",
            "error": str(exc),
        }

    # --------------------------------------------------
    # Overall readiness
    # --------------------------------------------------

    is_ready = all(
        check["status"] == "ready"
        for check in checks.values()
    )

    return {
        "status": (
            "ready"
            if is_ready
            else "not_ready"
        ),
        "checks": checks,
    }