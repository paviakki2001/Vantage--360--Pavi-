import threading
import time
from collections import defaultdict
from typing import Any


class MetricsCollector:

    def __init__(self):
        self._lock = threading.Lock()

        self.request_count = 0
        self.error_count = 0

        self.total_latency_ms = 0.0
        self.latency_samples = 0

        self.model_response_failures = defaultdict(int)
        self.orchestrator_failures = defaultdict(int)

        self.service_health = {}

        self.started_at = time.time()



    def record_request(
            self,
            latency_ms: float,
            status_code: int,
    ) -> None:

        with self._lock:

            self.request_count += 1

            self.total_latency_ms += latency_ms

            self.latency_samples += 1

            if status_code >= 500:
                self.error_count += 1



    def record_model_failure(
            self,
            model_name: str,
    ) -> None:

        with self._lock:
            self.model_response_failures[
                model_name
            ] += 1



    def record_orchestrator_failure(
            self,
            workflow_name: str,
    ) -> None:

        with self._lock:
            self.orchestrator_failures[
                workflow_name
            ] += 1


    def set_service_health(
            self,
            service_name: str,
            status: str,
    ) -> None:

        with self._lock:
            self.service_health[
                service_name
            ] = status

    def snapshot(self) -> dict[str, Any]:

        with self._lock:

            average_latency_ms = (
                self.total_latency_ms
                / self.latency_samples
                if self.latency_samples
                else 0.0
            )

            error_rate_percent = (
                (
                        self.error_count
                        / self.request_count
                )
                * 100
                if self.request_count
                else 0.0
            )

            uptime_seconds = (
                    time.time()
                    - self.started_at
            )

            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate_percent": round(
                    error_rate_percent,
                    2,
                ),
                "average_latency_ms": round(
                    average_latency_ms,
                    2,
                ),
                "api_availability_percent": (
                    round(
                        (
                                (
                                        self.request_count
                                        - self.error_count
                                )
                                / self.request_count
                        )
                        * 100,
                        2,
                        )
                    if self.request_count
                    else 100.0
                ),
                "model_response_failures": dict(
                    self.model_response_failures
                ),
                "orchestrator_failures": dict(
                    self.orchestrator_failures
                ),
                "service_health": dict(
                    self.service_health
                ),
                "uptime_seconds": round(
                    uptime_seconds,
                    2,
                ),
            }


metrics = MetricsCollector()