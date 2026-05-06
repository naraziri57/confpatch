"""Audit log support for confpatch — records every apply operation to a JSON-lines file."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_AUDIT_FILE = Path.home() / ".confpatch" / "audit.jsonl"


class AuditError(Exception):
    """Raised when audit log operations fail."""


@dataclass
class AuditEntry:
    config_file: str
    patch_keys: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user: str = field(default_factory=lambda: os.environ.get("USER", "unknown"))
    dry_run: bool = False
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def record(
    config_file: str,
    patch_keys: List[str],
    *,
    dry_run: bool = False,
    success: bool = True,
    error: Optional[str] = None,
    audit_path: Optional[Path] = None,
) -> AuditEntry:
    """Append a single audit entry to the audit log and return it."""
    entry = AuditEntry(
        config_file=str(config_file),
        patch_keys=list(patch_keys),
        dry_run=dry_run,
        success=success,
        error=error,
    )
    path = Path(audit_path) if audit_path else DEFAULT_AUDIT_FILE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict()) + "\n")
    except OSError as exc:
        raise AuditError(f"Failed to write audit log: {exc}") from exc
    return entry


def load_audit(audit_path: Optional[Path] = None) -> List[AuditEntry]:
    """Load all audit entries from the log file."""
    path = Path(audit_path) if audit_path else DEFAULT_AUDIT_FILE
    if not path.exists():
        return []
    entries: List[AuditEntry] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(AuditEntry.from_dict(json.loads(line)))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"Failed to read audit log: {exc}") from exc
    return entries
