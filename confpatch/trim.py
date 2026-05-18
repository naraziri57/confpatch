"""Trim leading/trailing whitespace from string values in a config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class TrimError(Exception):
    """Raised when trimming fails."""


@dataclass
class TrimResult:
    original: dict
    trimmed: dict
    changed_keys: list[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changed_keys)

    def count(self) -> int:
        return len(self.changed_keys)

    def summary(self) -> str:
        if not self.has_changes():
            return "No values trimmed."
        keys = ", ".join(self.changed_keys)
        return f"Trimmed {self.count()} value(s): {keys}"


def _trim_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _trim_dict(data: dict, prefix: str = "") -> tuple[dict, list[str]]:
    if not isinstance(data, dict):
        raise TrimError(f"Expected a dict, got {type(data).__name__}")

    result: dict = {}
    changed: list[str] = []

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            nested, nested_changed = _trim_dict(value, prefix=full_key)
            result[key] = nested
            changed.extend(nested_changed)
        elif isinstance(value, str):
            trimmed = value.strip()
            result[key] = trimmed
            if trimmed != value:
                changed.append(full_key)
        else:
            result[key] = value

    return result, changed


def trim_config(config: dict) -> TrimResult:
    """Return a new config with all string values stripped of surrounding whitespace."""
    if not isinstance(config, dict):
        raise TrimError(f"Config must be a dict, got {type(config).__name__}")

    trimmed, changed_keys = _trim_dict(config)
    return TrimResult(original=config, trimmed=trimmed, changed_keys=changed_keys)
