import logging
from typing import Any, Callable

from api.app.reliability.retry import RetryableError
from api.app.reliability.runner import execute_with_timeout

logger = logging.getLogger("vantage360-ai")


class ReliabilityManager:

    def __init__(
            self,
            max_attempts: int = 3,
            timeout_seconds: float = 10.0,
            retry_delay_seconds: float = 0.5,
    ):
        self.max_attempts = max_attempts
        self.timeout_seconds = timeout_seconds
        self.retry_delay_seconds = retry_delay_seconds

    def execute(
            self,
            operation: Callable[[], Any],
            operation_name: str,
            fallback: Any = None,
            retryable_exceptions: tuple[type[Exception], ...] = (
                    RetryableError,
                    TimeoutError,
            ),
    ) -> dict[str, Any]:

        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):

            try:
                result = execute_with_timeout(
                    operation,
                    self.timeout_seconds,
                )

                return {
                    "status": "success",
                    "data": result,
                    "attempts": attempt,
                }

            except retryable_exceptions as exc:
                last_error = exc

                logger.warning(
                    "Operation '%s' failed. "
                    "Attempt %s/%s. Error: %s",
                    operation_name,
                    attempt,
                    self.max_attempts,
                    exc,
                )

                if attempt < self.max_attempts:
                    import time

                    time.sleep(
                        self.retry_delay_seconds * (2 ** (attempt - 1))
                    )

            except Exception as exc:
                last_error = exc

                logger.exception(
                    "Non-retryable failure in operation '%s'.",
                    operation_name,
                )

                break

        logger.error(
            "Operation '%s' failed after %s attempts.",
            operation_name,
            self.max_attempts,
        )

        return {
            "status": "degraded",
            "data": fallback,
            "attempts": self.max_attempts,
            "error": {
                "code": self._get_error_code(last_error),
                "message": str(last_error)
                if last_error
                else "Unknown downstream failure.",
            },
        }

    @staticmethod
    def _get_error_code(error: Exception | None) -> str:
        if isinstance(error, TimeoutError):
            return "TIMEOUT_ERROR"

        if isinstance(error, RetryableError):
            return "DOWNSTREAM_ERROR"

        return "INTERNAL_ERROR"
