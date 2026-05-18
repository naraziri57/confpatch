"""Enforce required keys in a config, reporting any that are missing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class RequiredError(Exception):
    """Raised when required key validation fails unexpectedly."""


@dataclass
class RequiredResult:
    missing: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)

    def has_missing(self) -> bool:
        return len(self.missing) > 0

    def count(self) -> int:
        return len(self.missing)

    def summary(self) -> str:
        if not self.has_missing():
            return f"All {len(self.checked)} required key(s) present."
        keys = ", ".join(self.missing)
        return f"{len(self.missing)} required key(s) missing: {keys}"


def _get_nested(config: dict, key: str) -> Any:
    """Resolve a dot-notation key from a nested dict."""
    parts = key.split(".")
    current = config
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(key)
        current = current[part]
    return current


def check_required(config: dict, keys: list[str]) -> RequiredResult:
    """Check that all specified keys exist in the config.

    Args:
        config: The configuration dict to check.
        keys: List of dot-notation key paths that must be present.

    Returns:
        RequiredResult with any missing keys listed.
    """
    if not isinstance(config, dict):
        raise RequiredError("config must be a dict")

    missing = []
    for key in keys:
        try:
            _get_nested(config, key)
        except KeyError:
            missing.append(key)

    return RequiredResult(missing=missing, checked=list(keys))
