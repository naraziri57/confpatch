"""Track apply history for config patches."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_HISTORY_FILE = ".confpatch_history.json"


class HistoryError(Exception):
    """Raised when history operations fail."""


@dataclass
class HistoryEntry:
    timestamp: str
    config_file: str
    patch_file: str
    changes: list[dict[str, Any]]
    backup_path: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        config_file: str,
        patch_file: str,
        changes: list[dict[str, Any]],
        backup_path: str | None = None,
        tags: list[str] | None = None,
    ) -> "HistoryEntry":
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            config_file=str(config_file),
            patch_file=str(patch_file),
            changes=changes,
            backup_path=str(backup_path) if backup_path else None,
            tags=tags or [],
        )


def _history_path(directory: str | Path | None = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / DEFAULT_HISTORY_FILE


def load_history(directory: str | Path | None = None) -> list[HistoryEntry]:
    """Load all history entries from the history file."""
    path = _history_path(directory)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [HistoryEntry(**entry) for entry in data]
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise HistoryError(f"Failed to load history from {path}: {exc}") from exc


def append_history(
    entry: HistoryEntry,
    directory: str | Path | None = None,
) -> Path:
    """Append a new entry to the history file, creating it if needed."""
    path = _history_path(directory)
    entries = load_history(directory)
    entries.append(entry)
    path.write_text(
        json.dumps([asdict(e) for e in entries], indent=2),
        encoding="utf-8",
    )
    return path


def clear_history(directory: str | Path | None = None) -> None:
    """Delete the history file if it exists."""
    path = _history_path(directory)
    if path.exists():
        os.remove(path)
