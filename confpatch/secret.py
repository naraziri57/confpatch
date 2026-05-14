"""Mask and redact sensitive values in config patches."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

DEFAULT_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_\-]?key", re.IGNORECASE),
    re.compile(r"private[_\-]?key", re.IGNORECASE),
]

MASK = "***"


class SecretError(Exception):
    pass


@dataclass
class RedactResult:
    original_keys: list[str] = field(default_factory=list)
    redacted_keys: list[str] = field(default_factory=list)

    @property
    def redacted_count(self) -> int:
        return len(self.redacted_keys)

    def summary(self) -> str:
        if not self.redacted_keys:
            return "No sensitive keys redacted."
        keys = ", ".join(self.redacted_keys)
        return f"Redacted {self.redacted_count} sensitive key(s): {keys}"


def _is_sensitive(key: str, patterns: list[re.Pattern]) -> bool:
    return any(p.search(key) for p in patterns)


def redact_value(value: Any) -> Any:
    """Replace a value with the mask string if it's a non-empty scalar."""
    if isinstance(value, (dict, list)):
        return value
    return MASK


def redact_patch(
    patch: dict,
    patterns: list[re.Pattern] | None = None,
    prefix: str = "",
) -> tuple[dict, RedactResult]:
    """Return a copy of patch with sensitive values masked."""
    if not isinstance(patch, dict):
        raise SecretError("patch must be a dict")

    active_patterns = patterns if patterns is not None else DEFAULT_PATTERNS
    result = RedactResult()
    out: dict = {}

    for key, value in patch.items():
        full_key = f"{prefix}.{key}" if prefix else key
        result.original_keys.append(full_key)

        if isinstance(value, dict):
            nested, sub_result = redact_patch(value, active_patterns, prefix=full_key)
            out[key] = nested
            result.redacted_keys.extend(sub_result.redacted_keys)
            result.original_keys.extend(sub_result.original_keys)
        elif _is_sensitive(key, active_patterns):
            out[key] = redact_value(value)
            result.redacted_keys.append(full_key)
        else:
            out[key] = value

    return out, result
