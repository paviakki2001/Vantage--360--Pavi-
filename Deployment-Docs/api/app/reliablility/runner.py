import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable

from api.app.reliability.retry import RetryableError

logger = logging.getLogger("vantage360-ai")


class ReliabilityResult:

    def __init__(
            self,
            success: bool,
            data: Any = None,
            error_code: str | None = None,
            error_message: str | None = None,
            attempts: int = 0,
    ):
        self.success = success
        self.data = data
        self.error_code = error_code
        self.error_message = error_message
        self.attempts = attempts

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": (
                {
                    "code": self.error_code,
                    "message": self.error_message,
                }
                if self.error_code
                else None
            ),
            "attempts": self.attempts,
        }


def execute_with_timeout(
        func: Callable[[], Any],
        timeout_seconds: float,
) -> Any:

    executor = ThreadPoolExecutor(max_workers=1)

    future = executor.submit(func)

    try:
        return future.result(timeout=timeout_seconds)

    except TimeoutError as exc:
        future.cancel()

        logger.error(
            "Downstream operation timed out after %.2f seconds.",
            timeout_seconds,
        )

        raise TimeoutError(
            f"Downstream operation timed out after "
            f"{timeout_seconds} seconds."
        ) from exc

    finally:
        executor.shutdown(wait=False, cancel_futures=True)