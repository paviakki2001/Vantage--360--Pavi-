import logging

from api.app.data_access.Controlled_file import DatasetRepository
from api.app.services.churn_service import ChurnService
from api.app.reliability.reliability_manager import ReliabilityManager
from api.app.services.forecast_service import ForecastService
from api.app.services.recommendation_service import RecommendationService
from api.app.observability.workflow_tracer import WorkflowTracer


logger = logging.getLogger("vantage360-ai")


class CustomerIntelligenceService:

    TOOL_NAME = "customer_intelligence_brief"
    TOOL_VERSION = "v1"

    def __init__(self, repository: DatasetRepository):
        self.repository = repository
        self.churn_service = ChurnService(repository)
        self.forecast_service = ForecastService()
        self.recommendation_service = RecommendationService()

        self.reliability = ReliabilityManager(
            max_attempts=3,
            timeout_seconds=10.0,
            retry_delay_seconds=0.5,
        )

    def build_brief(self, customer_id: str, tracer: WorkflowTracer | None = None,) -> dict:

        normalized_customer_id = customer_id.strip().upper()

        if not normalized_customer_id:
            raise ValueError("customer_id is required.")

        if tracer is None:
            tracer = WorkflowTracer(
                workflow="customer_intelligence"
            )

        logger.info(
            "Building customer intelligence brief for customer_id=%s",
            normalized_customer_id,
        )

        # Churn scoring

        churn_start = tracer.start_step("churn")

        try:

            churn_execution = self.reliability.execute(
                operation=lambda: self.churn_service.predict(
                    normalized_customer_id
                ),
                operation_name="churn_scoring",
                fallback=None,
            )

            if churn_execution["status"] == "success":

                churn_result = churn_execution["data"]

                tracer.end_step(
                    step="churn",
                    start_time=churn_start,
                    status="success",
                )

            else:

                churn_result = {
                    "status": "degraded",
                    "message": (
                        "Churn scoring is temporarily unavailable."
                    ),
                    "reliability": churn_execution,
                }

                tracer.end_step(
                    step="churn",
                    start_time=churn_start,
                    status="failure",
                    error=churn_execution.get("error"),
                )

        except Exception as exc:

            tracer.end_step(
                step="churn",
                start_time=churn_start,
                status="failure",
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

            raise

        if churn_execution["status"] == "success":
            churn_result = churn_execution["data"]
        else:
            churn_result = {
                "status": "degraded",
                "message": "Churn scoring is temporarily unavailable.",
                "reliability": churn_execution,
            }

        # ---------------------------------------------------------
        # Revenue Forecast
        # ---------------------------------------------------------

        forecast_start = tracer.start_step(
            "revenue_forecast"
        )

        try:

            forecast_result = (
                self.forecast_service.get_forecast()
            )

            tracer.end_step(
                step="revenue_forecast",
                start_time=forecast_start,
                status="success",
            )

        except Exception as exc:

            tracer.end_step(
                step="revenue_forecast",
                start_time=forecast_start,
                status="failure",
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

            raise




        # ---------------------------------------------------------
        # Recommendation
        # ---------------------------------------------------------

        recommendation_start = tracer.start_step(
            "recommendation"
        )

        try:

            recommendation_result = (
                self.recommendation_service.get_recommendation(
                    normalized_customer_id
                )
            )

            tracer.end_step(
                step="recommendation",
                start_time=recommendation_start,
                status="success",
            )

        except Exception as exc:

            tracer.end_step(
                step="recommendation",
                start_time=recommendation_start,
                status="failure",
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

            raise

        brief = {
            "customer_id": normalized_customer_id,
            "churn": churn_result,
            "forecast": forecast_result,
            "recommendation": recommendation_result,
        }

        logger.info(
            "Customer intelligence brief built for customer_id=%s",
            normalized_customer_id,
        )

        return {
            **brief,
            "trace": tracer.to_dict(),
        }
