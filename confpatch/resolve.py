"""Resolve references to external files or URLs into inline config values."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ResolveError(Exception):
    pass


@dataclass
class ResolveResult:
    resolved: dict
    changes: list[tuple[str, str]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.has_changes():
            return "No references resolved."
        lines = [f"Resolved {self.count()} reference(s):"]
        for key, ref in self.changes:
            lines.append(f"  {key}: {ref}")
        return "\n".join(lines)


def _read_file_ref(ref: str, base_dir: Path) -> str:
    """Read content from a file:// reference."""
    path_str = ref[len("file://"):]
    path = base_dir / path_str if not Path(path_str).is_absolute() else Path(path_str)
    if not path.exists():
        raise ResolveError(f"Referenced file not found: {path}")
    return path.read_text().strip()


def _resolve_value(value: Any, base_dir: Path) -> tuple[Any, bool]:
    """Return (resolved_value, was_changed)."""
    if isinstance(value, str) and value.startswith("file://"):
        return _read_file_ref(value, base_dir), True
    return value, False


def _walk(config: Any, base_dir: Path, prefix: str, changes: list) -> Any:
    if isinstance(config, dict):
        result = {}
        for k, v in config.items():
            full_key = f"{prefix}.{k}" if prefix else k
            resolved, changed = _resolve_value(v, base_dir)
            if changed:
                changes.append((full_key, v))
                result[k] = resolved
            else:
                result[k] = _walk(v, base_dir, full_key, changes)
        return result
    if isinstance(config, list):
        return [_walk(item, base_dir, prefix, changes) for item in config]
    return config


def resolve_refs(config: dict, base_dir: str | Path = ".") -> ResolveResult:
    """Walk config and replace file:// references with file contents."""
    if not isinstance(config, dict):
        raise ResolveError("Config must be a dict.")
    base = Path(base_dir)
    changes: list[tuple[str, str]] = []
    resolved = _walk(copy.deepcopy(config), base, "", changes)
    return ResolveResult(resolved=resolved, changes=changes)
