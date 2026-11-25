import time
from collections import defaultdict
from threading import Lock


class RateLimiter:

    def __init__(
            self,
            max_requests: int = 60,
            window_seconds: int = 60,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self._requests = defaultdict(list)
        self._lock = Lock()

    def is_allowed(
            self,
            client_id: str,
    ) -> bool:

        now = time.monotonic()

        with self._lock:

            timestamps = self._requests[client_id]

            cutoff = (
                    now - self.window_seconds
            )

            timestamps[:] = [
                timestamp
                for timestamp in timestamps
                if timestamp > cutoff
            ]

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)

            return True