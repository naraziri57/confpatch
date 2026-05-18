"""Clamp numeric values in a config to a specified range."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ClampError(Exception):
    pass


@dataclass
class ClampResult:
    clamped: dict[str, Any]
    changes: list[tuple[str, Any, Any]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.has_changes():
            return "No values clamped."
        lines = [f"Clamped {self.count()} value(s):"]
        for key, old, new in self.changes:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _clamp_value(value: Any, min_val: float | None, max_val: float | None) -> Any:
    if not isinstance(value, (int, float)):
        return value
    if min_val is not None and value < min_val:
        return type(value)(min_val)
    if max_val is not None and value > max_val:
        return type(value)(max_val)
    return value


def clamp_config(
    config: dict,
    min_val: float | None = None,
    max_val: float | None = None,
    keys: list[str] | None = None,
    prefix: str = "",
) -> ClampResult:
    """Recursively clamp numeric values in config within [min_val, max_val]."""
    if not isinstance(config, dict):
        raise ClampError("Config must be a dict.")
    if min_val is not None and max_val is not None and min_val > max_val:
        raise ClampError(f"min_val ({min_val}) must not exceed max_val ({max_val}).")

    result: dict = {}
    changes: list[tuple[str, Any, Any]] = []

    for k, v in config.items():
        full_key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
        if isinstance(v, dict):
            sub = clamp_config(v, min_val=min_val, max_val=max_val, keys=keys, prefix=full_key)
            result[k] = sub.clamped
            changes.extend(sub.changes)
        else:
            if keys is None or full_key in keys:
                new_v = _clamp_value(v, min_val, max_val)
                result[k] = new_v
                if new_v != v:
                    changes.append((full_key, v, new_v))
            else:
                result[k] = v

    return ClampResult(clamped=result, changes=changes)
