"""Rate limiter (docs/SPEC.md §5.6)."""

from __future__ import annotations

import threading
import time


class RateLimiter:
    def __init__(self, min_interval_s: float) -> None:
        self._min_interval_s = min_interval_s
        self._lock = threading.Lock()
        self._last_return: float | None = None

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if self._last_return is not None:
                elapsed = now - self._last_return
                remaining = self._min_interval_s - elapsed
                if remaining > 0:
                    time.sleep(remaining)
            self._last_return = time.monotonic()

    def backoff(self, attempt: int) -> None:
        time.sleep(30 * (2**attempt))
