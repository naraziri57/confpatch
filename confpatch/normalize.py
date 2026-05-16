"""Key normalization utilities for confpatch."""

from __future__ import annotations

import re
from typing import Any


class NormalizeError(Exception):
    """Raised when normalization fails."""


_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _to_snake(key: str) -> str:
    """Convert camelCase or PascalCase key to snake_case."""
    return _CAMEL_RE.sub("_", key).lower()


def _to_kebab(key: str) -> str:
    """Convert a key to kebab-case."""
    return _to_snake(key).replace("_", "-")


def _normalize_key(key: str, style: str) -> str:
    """Normalize a single key to the given style."""
    if style == "snake":
        return _to_snake(key)
    if style == "kebab":
        return _to_kebab(key)
    if style == "lower":
        return key.lower()
    if style == "upper":
        return key.upper()
    raise NormalizeError(f"Unknown normalization style: {style!r}")


def normalize_keys(data: dict[str, Any], style: str = "snake") -> dict[str, Any]:
    """Recursively normalize all keys in a dict to the given style.

    Supported styles: 'snake', 'kebab', 'lower', 'upper'.
    """
    if not isinstance(data, dict):
        raise NormalizeError(f"Expected dict, got {type(data).__name__}")
    result: dict[str, Any] = {}
    for key, value in data.items():
        normalized = _normalize_key(str(key), style)
        if isinstance(value, dict):
            result[normalized] = normalize_keys(value, style)
        else:
            result[normalized] = value
    return result


def normalize_patch(patch: dict[str, Any], style: str = "snake") -> dict[str, Any]:
    """Return a copy of patch with all keys normalized."""
    return normalize_keys(patch, style)
