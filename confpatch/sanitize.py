"""Sanitize config values by stripping whitespace and normalizing strings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SanitizeError(Exception):
    """Raised when sanitization fails."""


@dataclass
class SanitizeResult:
    cleaned: dict
    changes: list[tuple[str, Any, Any]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.has_changes():
            return "No sanitization changes."
        lines = [f"Sanitized {self.count()} value(s):"]
        for key, old, new in self.changes:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _sanitize_value(value: Any, strip: bool, lowercase: bool, collapse: bool) -> Any:
    """Apply sanitization transforms to a single string value."""
    if not isinstance(value, str):
        return value
    result = value
    if strip:
        result = result.strip()
    if collapse:
        import re
        result = re.sub(r"\s+", " ", result)
    if lowercase:
        result = result.lower()
    return result


def sanitize_config(
    config: dict,
    strip: bool = True,
    lowercase: bool = False,
    collapse: bool = False,
    prefix: str = "",
) -> SanitizeResult:
    """Recursively sanitize all string values in a config dict."""
    if not isinstance(config, dict):
        raise SanitizeError(f"Expected dict, got {type(config).__name__}")

    cleaned: dict = {}
    changes: list[tuple[str, Any, Any]] = []

    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            sub = sanitize_config(value, strip=strip, lowercase=lowercase,
                                  collapse=collapse, prefix=full_key)
            cleaned[key] = sub.cleaned
            changes.extend(sub.changes)
        else:
            new_value = _sanitize_value(value, strip=strip, lowercase=lowercase,
                                        collapse=collapse)
            cleaned[key] = new_value
            if new_value != value:
                changes.append((full_key, value, new_value))

    return SanitizeResult(cleaned=cleaned, changes=changes)
