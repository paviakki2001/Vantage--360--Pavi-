import logging

from orchestration.agents.autonomous_insight_orchestrator import (
    AutonomousInsightOrchestrator,
)

logger = logging.getLogger("vantage360-ai")


class AutonomousInsightWorkflow:

    def __init__(
            self,
            orchestrator: AutonomousInsightOrchestrator,
    ):
        self.orchestrator = orchestrator

    def run(
            self,
            kpi_event: dict,
    ) -> dict:

        if not kpi_event:
            raise ValueError(
                "kpi_event is required."
            )

        logger.info(
            "Starting autonomous insight workflow."
        )

        result = self.orchestrator.investigate(
            kpi_event
        )

        logger.info(
            "Autonomous insight workflow completed."
        )

        return result