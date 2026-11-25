import time
import uuid
from typing import Any


class WorkflowTracer:

    def __init__(
            self,
            correlation_id: str | None = None,
            workflow: str = "unknown",
    ):
        self.correlation_id = (
                correlation_id
                or str(uuid.uuid4())
        )

        self.workflow = workflow
        self.steps: list[dict[str, Any]] = []

    def start_step(self, step: str) -> float:

        return time.perf_counter()

    def end_step(
            self,
            step: str,
            start_time: float,
            status: str,
            error: dict[str, Any] | None = None,
    ) -> None:

        duration_ms = (
                              time.perf_counter() - start_time
                      ) * 1000

        self.steps.append(
            {
                "step": step,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
                "status": status,
                "error": error,
            }
        )

    def add_step(
            self,
            step: str,
            status: str,
            duration_ms: float = 0.0,
            error: dict[str, Any] | None = None,
    ) -> None:

        self.steps.append(
            {
                "step": step,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
                "status": status,
                "error": error,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "workflow": self.workflow,
            "steps": self.steps,
        }