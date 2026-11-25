import logging
import time
from typing import Callable, TypeVar

logger = logging.getLogger("vantage360-ai")

T = TypeVar("T")


class RetryableError(Exception):
    """Exception indicating that an operation can safely be retried"""


def retry(
        max_attempts: int = 3,
        delay_seconds: float = 0.5,
        backoff_multiplier: float = 2.0,
):


    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            delay = delay_seconds

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except RetryableError as exc:
                    if attempt == max_attempts:
                        logger.error(
                            "Retry limit reached for %s after %s attempts.",
                            func.__name__,
                            max_attempts,
                        )
                        raise

                    logger.warning(
                        "Retryable failure in %s. "
                        "Attempt %s/%s. Retrying in %.2fs. Error: %s",
                        func.__name__,
                        attempt,
                        max_attempts,
                        delay,
                        exc,
                    )

                    time.sleep(delay)
                    delay *= backoff_multiplier

        return wrapper

    return decorator
