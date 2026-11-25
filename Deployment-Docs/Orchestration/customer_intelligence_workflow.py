import logging
from api.app.observability.workflow_tracer import WorkflowTracer
from api.app.errors import AppException
from api.app.reliability.exceptions import OrchestratorFailureError


logger = logging.getLogger("vantage360-ai")


class CustomerIntelligenceWorkflow:

    def __init__(self, intelligence_service):
        self.intelligence_service = intelligence_service

    def run(
            self,
            customer_id: str,
            correlation_id: str | None = None,
    ) -> dict:

        if not customer_id or not customer_id.strip():
            raise ValueError(
                "customer_id is required."
            )

        normalized_customer_id = (
            customer_id.strip().upper()
        )

        tracer = WorkflowTracer(
            correlation_id=correlation_id,
            workflow="customer_intelligence",
        )

        logger.info(
            "Starting customer intelligence workflow "
            "correlation_id=%s customer_id=%s",
            tracer.correlation_id,
            normalized_customer_id,
        )

        start_time = tracer.start_step(
            "orchestrator"
        )

        try:

            result = (
                self.intelligence_service.build_brief(
                    normalized_customer_id,
                    tracer=tracer,
                )
            )

            tracer.end_step(
                step="orchestrator",
                start_time=start_time,
                status="success",
            )

        except AppException as exc:

            tracer.end_step(
                step="orchestrator",
                start_time=start_time,
                status="failure",
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "code": exc.code,
                },
            )

            logger.warning(
                "Customer intelligence workflow failed "
                "with application error "
                "correlation_id=%s code=%s",
                tracer.correlation_id,
                exc.code,
            )

            raise

        except Exception as exc:


            tracer.end_step(
                step="orchestrator",
                start_time=start_time,
                status="failure",
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

            logger.exception(
                "Customer intelligence workflow failed "
                "correlation_id=%s",
                tracer.correlation_id,
            )

            raise OrchestratorFailureError(
                tool="customer_intelligence",
                version="v2",
                message=(
                    "Customer intelligence orchestration failed."
                ),
                details={
                    "workflow": "customer_intelligence",
                    "customer_id": normalized_customer_id,
                    "correlation_id": (
                        tracer.correlation_id
                    ),
                },
            ) from exc

        logger.info(
            "Customer intelligence workflow completed "
            "correlation_id=%s customer_id=%s",
            tracer.correlation_id,
            normalized_customer_id,
        )

        return {
            **result,
            "trace": tracer.to_dict(),
        }
