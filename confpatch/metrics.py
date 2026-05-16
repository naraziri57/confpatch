"""Track and report patch application metrics."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class MetricsError(Exception):
    pass


@dataclass
class MetricEntry:
    config_file: str
    patch_file: str
    keys_changed: int
    duration_ms: float
    success: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "config_file": self.config_file,
            "patch_file": self.patch_file,
            "keys_changed": self.keys_changed,
            "duration_ms": round(self.duration_ms, 3),
            "success": self.success,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MetricEntry":
        return cls(
            config_file=data["config_file"],
            patch_file=data["patch_file"],
            keys_changed=data["keys_changed"],
            duration_ms=data["duration_ms"],
            success=data["success"],
            timestamp=data["timestamp"],
        )


def _metrics_path(config_file: str) -> Path:
    base = Path(config_file)
    return base.parent / ".confpatch" / f"{base.name}.metrics.json"


def load_metrics(config_file: str) -> List[MetricEntry]:
    path = _metrics_path(config_file)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return [MetricEntry.from_dict(e) for e in data]
    except Exception as exc:
        raise MetricsError(f"Failed to load metrics: {exc}") from exc


def record_metric(entry: MetricEntry) -> MetricEntry:
    path = _metrics_path(entry.config_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_metrics(entry.config_file)
    existing.append(entry)
    try:
        path.write_text(json.dumps([e.to_dict() for e in existing], indent=2))
    except Exception as exc:
        raise MetricsError(f"Failed to write metrics: {exc}") from exc
    return entry


def summarize_metrics(config_file: str) -> dict:
    entries = load_metrics(config_file)
    if not entries:
        return {"total": 0, "successful": 0, "failed": 0, "avg_duration_ms": 0.0, "total_keys_changed": 0}
    successful = [e for e in entries if e.success]
    avg_dur = sum(e.duration_ms for e in entries) / len(entries)
    return {
        "total": len(entries),
        "successful": len(successful),
        "failed": len(entries) - len(successful),
        "avg_duration_ms": round(avg_dur, 3),
        "total_keys_changed": sum(e.keys_changed for e in entries),
    }
