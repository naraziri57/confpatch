"""Truncate long string values in a config to a maximum length."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class TruncateError(Exception):
    """Raised when truncation fails."""


@dataclass
class TruncateResult:
    truncated_keys: list[str] = field(default_factory=list)
    original_lengths: dict[str, int] = field(default_factory=dict)

    @property
    def has_truncations(self) -> bool:
        return len(self.truncated_keys) > 0

    @property
    def count(self) -> int:
        return len(self.truncated_keys)

    def summary(self) -> str:
        if not self.has_truncations:
            return "No values truncated."
        lines = [f"Truncated {self.count} value(s):"]
        for key in self.truncated_keys:
            orig = self.original_lengths.get(key, "?")
            lines.append(f"  {key}: {orig} chars")
        return "\n".join(lines)


def _truncate_value(value: Any, max_length: int, suffix: str) -> tuple[Any, bool]:
    """Return (possibly truncated value, was_truncated)."""
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length] + suffix, True
    return value, False


def truncate_config(
    config: dict,
    max_length: int = 80,
    suffix: str = "...",
    prefix: str = "",
) -> tuple[dict, TruncateResult]:
    """Recursively truncate all string values longer than max_length.

    Returns a new config dict and a TruncateResult describing what changed.
    """
    if not isinstance(config, dict):
        raise TruncateError("config must be a dict")
    if max_length < 1:
        raise TruncateError("max_length must be at least 1")

    result = TruncateResult()
    out: dict = {}

    for key, value in config.items():
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            out[key], sub = truncate_config(value, max_length, suffix, full_key)
            result.truncated_keys.extend(sub.truncated_keys)
            result.original_lengths.update(sub.original_lengths)
        else:
            new_val, was_truncated = _truncate_value(value, max_length, suffix)
            out[key] = new_val
            if was_truncated:
                result.truncated_keys.append(full_key)
                result.original_lengths[full_key] = len(value)

    return out, result
