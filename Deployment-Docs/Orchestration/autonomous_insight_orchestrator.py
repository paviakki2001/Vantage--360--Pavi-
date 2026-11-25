import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from api.app.integrations.service_client import ServiceClient
from api.app.observability.metrics import metrics


logger = logging.getLogger("vantage360-ai")


class AutonomousInsightOrchestrator:
    def __init__(
            self,
            service_client: ServiceClient | None = None,
            analytics_service=None,
    ):

        self.analytics_service = analytics_service
        self.service_client = service_client or ServiceClient()
        self.churn_service = self.service_client
        self.forecast_service = self.service_client
        self.recommendation_service = self.service_client

    def investigate(
            self,
            kpi_event: dict[str, Any],
    ) -> dict[str, Any]:
        correlation_id = str(uuid.uuid4())

        logger.info(
            "Starting autonomous insight investigation "
            "correlation_id=%s",
            correlation_id,
        )
        try:

            investigation_request = (
                self._build_investigation_request(
                    kpi_event
                )
            )

            analytics_context = (
                self._run_analytics(
                    investigation_request
                )
            )

            ml_context = (
                self._run_ml_services(
                    investigation_request
                )
            )

            context = self._aggregate_context(
                kpi_event=kpi_event,
                investigation_request=investigation_request,
                analytics_context=analytics_context,
                ml_context=ml_context,
            )

            insight_payload = (
                self._build_insight_payload(
                    correlation_id=correlation_id,
                    context=context,
                )
            )

            logger.info(
                "Autonomous insight investigation completed "
                "correlation_id=%s",
                correlation_id,
            )

            return insight_payload

        except Exception:
            metrics.record_orchestrator_failure(
                "autonomous_insight"
            )

            logger.exception(
                "Autonomous insight investigation failed "
                "correlation_id=%s",
                correlation_id,
            )
        raise
    def _build_investigation_request(
            self,
            kpi_event: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "investigation_id": str(uuid.uuid4()),
            "kpi_name": kpi_event.get("kpi_name"),
            "customer_id": kpi_event.get("customer_id"),
            "current_value": kpi_event.get("current_value"),
            "previous_value": kpi_event.get("previous_value"),
            "change_percent": kpi_event.get("change_percent"),
            "event_type": kpi_event.get("event_type"),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def _run_analytics(
            self,
            investigation_request: dict[str, Any],
    ) -> dict[str, Any]:

        if self.analytics_service is None:
            logger.info(
                "Analytics service not configured; "
                "returning empty analytical context."
            )
            return {}

        try:
            return self.analytics_service.investigate(
                investigation_request
            )
        except Exception:
            logger.exception(
                "Analytics service failed."
            )
            return {
                "status": "failed",
                "error": "Analytics service failed.",
            }

    def _run_ml_services(
            self,
            investigation_request: dict[str, Any],
    ) -> dict[str, Any]:

        customer_id = investigation_request.get(
            "customer_id"
        )

        ml_context: dict[str, Any] = {}

        # Churn
        if self.churn_service is not None and customer_id:
            try:
                ml_context["churn"] = (
                    self.service_client.predict_churn(
                        customer_id
                    )
                )
            except Exception:
                logger.exception(
                    "Churn service failed."
                )
                ml_context["churn"] = {
                    "status": "failed",
                    "error": "Churn service failed.",
                }

        # Forecast

        try:
            ml_context["forecast"] = (
                self.service_client.get_forecast()
            )
        except Exception:
            logger.exception(
                "Forecast service failed."
            )
            ml_context["forecast"] = {
                "status": "failed",
                "error": "Forecast service failed.",
            }

        # Recommendation
        if customer_id:
            try:
                ml_context["recommendation"] = (
                    self.service_client.get_recommendation(
                        customer_id
                    )
                )
            except Exception:
                logger.exception(
                    "Recommendation service failed."
                )
                ml_context["recommendation"] = {
                    "status": "failed",
                    "error": "Recommendation service failed.",
                }

        return ml_context

    def _aggregate_context(
            self,
            kpi_event: dict[str, Any],
            investigation_request: dict[str, Any],
            analytics_context: dict[str, Any],
            ml_context: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "kpi_event": kpi_event,
            "investigation_request": investigation_request,
            "analytics": analytics_context,
            "machine_learning": ml_context,
        }

    def _build_insight_payload(
            self,
            correlation_id: str,
            context: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "correlation_id": correlation_id,
            "status": "success",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "context": context,
            "genai_ready": True,
        }