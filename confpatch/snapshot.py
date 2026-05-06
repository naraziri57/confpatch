"""Snapshot support: capture and compare full config state at a point in time."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class SnapshotError(Exception):
    pass


@dataclass
class Snapshot:
    config_path: str
    data: dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "config_path": self.config_path,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Snapshot":
        return cls(
            config_path=d["config_path"],
            data=d["data"],
            timestamp=d["timestamp"],
        )


def _snapshot_path(config_path: Path, snapshot_dir: Path) -> Path:
    safe_name = config_path.name.replace(".", "_")
    return snapshot_dir / f"{safe_name}.snapshots.json"


def save_snapshot(config_path: Path, data: dict, snapshot_dir: Path | None = None) -> Snapshot:
    """Save a snapshot of the given config data."""
    if not config_path.exists():
        raise SnapshotError(f"Config file not found: {config_path}")

    snapshot_dir = snapshot_dir or config_path.parent / ".confpatch_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    snap = Snapshot(config_path=str(config_path), data=data)
    snap_file = _snapshot_path(config_path, snapshot_dir)

    existing = load_snapshots(config_path, snapshot_dir)
    existing.append(snap)

    snap_file.write_text(
        json.dumps([s.to_dict() for s in existing], indent=2),
        encoding="utf-8",
    )
    return snap


def load_snapshots(config_path: Path, snapshot_dir: Path | None = None) -> list[Snapshot]:
    """Load all snapshots for a given config file."""
    snapshot_dir = snapshot_dir or config_path.parent / ".confpatch_snapshots"
    snap_file = _snapshot_path(config_path, snapshot_dir)

    if not snap_file.exists():
        return []

    try:
        raw = json.loads(snap_file.read_text(encoding="utf-8"))
        return [Snapshot.from_dict(entry) for entry in raw]
    except (json.JSONDecodeError, KeyError) as exc:
        raise SnapshotError(f"Failed to load snapshots: {exc}") from exc


def get_latest_snapshot(config_path: Path, snapshot_dir: Path | None = None) -> Snapshot | None:
    """Return the most recent snapshot for a config file, or None."""
    snaps = load_snapshots(config_path, snapshot_dir)
    return snaps[-1] if snaps else None
