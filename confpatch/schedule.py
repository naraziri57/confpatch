"""Scheduled patch execution — run patches at a given time or after a delay."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional


class ScheduleError(Exception):
    """Raised when a scheduled patch fails."""


@dataclass
class ScheduleResult:
    config_file: str
    patch_file: str
    ran_at: datetime
    success: bool
    message: str = ""

    def summary(self) -> str:
        status = "OK" if self.success else "FAILED"
        ts = self.ran_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{status}] {self.patch_file} -> {self.config_file} at {ts}: {self.message}"


def run_at(
    target_time: datetime,
    config_file: str,
    patch_file: str,
    apply_fn: Callable[[str, str], None],
    *,
    poll_interval: float = 1.0,
) -> ScheduleResult:
    """Block until target_time, then apply the patch."""
    now = datetime.now()
    delay = (target_time - now).total_seconds()
    if delay < 0:
        raise ScheduleError(
            f"Target time {target_time} is in the past (now={now})"
        )
    time.sleep(delay)
    return _execute(config_file, patch_file, apply_fn)


def run_after(
    seconds: float,
    config_file: str,
    patch_file: str,
    apply_fn: Callable[[str, str], None],
) -> ScheduleResult:
    """Wait `seconds` then apply the patch."""
    if seconds < 0:
        raise ScheduleError("Delay must be non-negative.")
    time.sleep(seconds)
    return _execute(config_file, patch_file, apply_fn)


def _execute(
    config_file: str,
    patch_file: str,
    apply_fn: Callable[[str, str], None],
) -> ScheduleResult:
    ran_at = datetime.now()
    try:
        apply_fn(config_file, patch_file)
        return ScheduleResult(
            config_file=config_file,
            patch_file=patch_file,
            ran_at=ran_at,
            success=True,
            message="patch applied",
        )
    except Exception as exc:  # noqa: BLE001
        return ScheduleResult(
            config_file=config_file,
            patch_file=patch_file,
            ran_at=ran_at,
            success=False,
            message=str(exc),
        )
