"""Backup and restore utilities for config files before patching."""

import shutil
import os
from datetime import datetime
from pathlib import Path


class BackupError(Exception):
    pass


def create_backup(filepath: str, backup_dir: str | None = None) -> str:
    """
    Create a timestamped backup of the given file.

    Returns the path to the backup file.
    """
    source = Path(filepath)
    if not source.exists():
        raise BackupError(f"File not found: {filepath}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.stem}.{timestamp}.bak{source.suffix}"

    if backup_dir:
        dest_dir = Path(backup_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / backup_name
    else:
        dest = source.parent / backup_name

    shutil.copy2(source, dest)
    return str(dest)


def restore_backup(backup_path: str, target_path: str) -> None:
    """
    Restore a backup file to the target path, overwriting it.
    """
    backup = Path(backup_path)
    if not backup.exists():
        raise BackupError(f"Backup file not found: {backup_path}")

    shutil.copy2(backup, target_path)


def list_backups(filepath: str, backup_dir: str | None = None) -> list[str]:
    """
    List all backup files associated with a given config file.
    """
    source = Path(filepath)
    search_dir = Path(backup_dir) if backup_dir else source.parent

    if not search_dir.exists():
        return []

    pattern = f"{source.stem}.*.bak{source.suffix}"
    backups = sorted(search_dir.glob(pattern))
    return [str(p) for p in backups]


def delete_backup(backup_path: str) -> None:
    """
    Delete a specific backup file.
    """
    path = Path(backup_path)
    if not path.exists():
        raise BackupError(f"Backup file not found: {backup_path}")
    os.remove(path)
