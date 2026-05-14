"""Notification hooks for post-apply events (stdout, file, or custom callback)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional


class NotifyError(Exception):
    pass


@dataclass
class NotifyEvent:
    config_file: str
    patch_file: str
    changed_keys: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success: bool = True
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "config_file": self.config_file,
            "patch_file": self.patch_file,
            "changed_keys": self.changed_keys,
            "timestamp": self.timestamp,
            "success": self.success,
            "message": self.message,
        }


def notify_stdout(event: NotifyEvent) -> None:
    """Print a notification summary to stdout."""
    status = "OK" if event.success else "FAILED"
    keys = ", ".join(event.changed_keys) if event.changed_keys else "(none)"
    print(f"[confpatch] [{status}] {event.config_file} <- {event.patch_file} | keys: {keys}")
    if event.message:
        print(f"  {event.message}")


def notify_file(event: NotifyEvent, log_path: Path) -> None:
    """Append a JSON notification entry to a log file."""
    try:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    except OSError as e:
        raise NotifyError(f"Failed to write notification log: {e}") from e


def dispatch(
    event: NotifyEvent,
    *,
    stdout: bool = False,
    log_path: Optional[Path] = None,
    callback: Optional[Callable[[NotifyEvent], None]] = None,
) -> None:
    """Dispatch a NotifyEvent to all configured channels."""
    if stdout:
        notify_stdout(event)
    if log_path is not None:
        notify_file(event, log_path)
    if callback is not None:
        try:
            callback(event)
        except Exception as e:
            raise NotifyError(f"Notification callback raised: {e}") from e
