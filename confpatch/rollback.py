"""Rollback support: undo the last applied patch using history + backup."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from confpatch.backup import restore_backup, BackupError
from confpatch.history import load_history, HistoryError


class RollbackError(Exception):
    """Raised when a rollback operation fails."""


def get_last_entry(config_path: Path):
    """Return the most recent history entry for the given config file."""
    try:
        entries = load_history(config_path)
    except HistoryError as exc:
        raise RollbackError(f"Could not load history: {exc}") from exc

    if not entries:
        raise RollbackError(f"No history found for {config_path}")

    return entries[-1]


def rollback(config_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """Restore the config file to its state before the last patch.

    Returns the path of the restored file.
    Raises RollbackError if rollback is not possible.
    """
    entry = get_last_entry(config_path)

    backup_path = Path(entry.backup_path) if entry.backup_path else None
    if backup_path is None:
        raise RollbackError(
            f"History entry for {config_path} has no associated backup."
        )

    if not backup_path.exists():
        raise RollbackError(
            f"Backup file not found: {backup_path}. Cannot rollback."
        )

    try:
        restored = restore_backup(backup_path, config_path)
    except BackupError as exc:
        raise RollbackError(f"Restore failed: {exc}") from exc

    return restored
