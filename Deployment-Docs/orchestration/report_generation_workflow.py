import logging
from typing import Any

logger = logging.getLogger("vantage360-ai")


class ReportGenerationWorkflow:

    def __init__(self, report_service):
        self.report_service = report_service

    def run(
            self,
            model_outputs: dict[str, Any],
            kpi_snapshot: dict[str, Any],
            business_context: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(model_outputs, dict):
            raise ValueError(
                "model_outputs must be a dictionary."
            )

        if not isinstance(kpi_snapshot, dict):
            raise ValueError(
                "kpi_snapshot must be a dictionary."
            )

        if not isinstance(business_context, dict):
            raise ValueError(
                "business_context must be a dictionary."
            )

        logger.info(
            "Starting report generation workflow."
        )

        result = self.report_service.generate_report(
            model_outputs=model_outputs,
            kpi_snapshot=kpi_snapshot,
            business_context=business_context,
        )

        logger.info(
            "Report generation workflow completed."
        )

        return result
