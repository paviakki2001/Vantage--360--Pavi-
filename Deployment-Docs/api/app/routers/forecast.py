
from functools import lru_cache

from fastapi import APIRouter, Depends
import logging
from api.app.errors import AppException
from api.app.services.forecast_service import ForecastService
from datetime import datetime, timezone
from api.app.schemas.model_api import (
    ForecastRequest,
    StandardModelResponse,
)
from api.app.services.forecast_service import (
    ForecastService,
)

from api.app.gateway.authentication import (
    require_api_key,
)
from api.app.observability.metrics import metrics


logger = logging.getLogger("vantage360-ai")

router = APIRouter(
    prefix="/forecast",
    tags=["Revenue Forecast"],
    dependencies=[
        Depends(require_api_key)
    ],
)


@lru_cache
def get_forecast_service() -> ForecastService:
    return ForecastService()

@router.post(
    "/predict",
    response_model=StandardModelResponse,
)
def predict_forecast(
        request: ForecastRequest,
        forecast_service: ForecastService = Depends(
            get_forecast_service
        ),
):

    logger.info(
        "Revenue forecast request received"
    )

    try:

        result = forecast_service.get_forecast()

        timestamp = (
            datetime.now(timezone.utc).isoformat()
        )

        logger.info(
            "Revenue forecast completed "
            "model_version=%s",
            result.get("model_version"),
        )

        return {
            "tool": "revenue_forecast",
            "version": "v1",
            "input": {},
            "output": result,
            "metadata": {
                "model_version": result.get(
                    "model_version"
                ),
                "forecast_horizon": result.get(
                    "forecast_horizon"
                ),
            },
            "status": "success",
            "timestamp": timestamp,
        }

    except ValueError as exc:

        logger.warning(
            "Revenue forecast validation failure: %s",
            exc,
        )

        raise AppException(
            message=str(exc),
            status_code=400,
        ) from exc

    except TimeoutError as exc:

        logger.error(
            "Revenue forecast timeout"
        )

        raise AppException(
            message="Revenue forecast timed out.",
            status_code=504,
        ) from exc

    except Exception as exc:
        metrics.record_model_failure(
            "forecast"
        )

        logger.exception(
            "Revenue forecast failed"
        )

        raise AppException(
            message="Revenue forecast failed.",
            status_code=500,
        ) from exc
