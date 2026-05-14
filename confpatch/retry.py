"""Retry logic for applying patches with configurable attempts and backoff."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Any


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, attempts: int, last_error: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


@dataclass
class RetryResult:
    success: bool
    attempts: int
    value: Any = None
    error: Exception | None = None
    durations: list[float] = field(default_factory=list)

    def summary(self) -> str:
        status = "succeeded" if self.success else "failed"
        return (
            f"Operation {status} after {self.attempts} attempt(s); "
            f"total time: {sum(self.durations):.3f}s"
        )


def retry(
    fn: Callable[[], Any],
    *,
    attempts: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> RetryResult:
    """Call *fn* up to *attempts* times, with exponential backoff.

    Args:
        fn: Zero-argument callable to execute.
        attempts: Maximum number of tries.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier applied to delay after each failure.
        exceptions: Exception types that trigger a retry.

    Returns:
        RetryResult describing the outcome.

    Raises:
        RetryError: If all attempts fail.
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_exc: Exception | None = None
    durations: list[float] = []
    current_delay = delay

    for attempt in range(1, attempts + 1):
        t0 = time.monotonic()
        try:
            result = fn()
            durations.append(time.monotonic() - t0)
            return RetryResult(
                success=True,
                attempts=attempt,
                value=result,
                durations=durations,
            )
        except exceptions as exc:  # type: ignore[misc]
            durations.append(time.monotonic() - t0)
            last_exc = exc
            if attempt < attempts:
                time.sleep(current_delay)
                current_delay *= backoff

    raise RetryError(
        f"All {attempts} attempt(s) failed: {last_exc}",
        attempts=attempts,
        last_error=last_exc,  # type: ignore[arg-type]
    )
