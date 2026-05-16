"""Flatten nested config dicts into dot-notation key-value pairs."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class FlattenError(Exception):
    """Raised when flattening fails."""


@dataclass
class FlattenResult:
    flat: dict[str, Any]
    original_keys: int
    flat_keys: int

    def summary(self) -> str:
        return (
            f"Flattened {self.original_keys} top-level key(s) "
            f"into {self.flat_keys} dot-notation key(s)."
        )


def _flatten(data: Any, prefix: str = "", sep: str = ".") -> dict[str, Any]:
    """Recursively flatten a nested dict."""
    if not isinstance(data, dict):
        raise FlattenError(f"Expected a dict, got {type(data).__name__}")

    result: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten(value, prefix=full_key, sep=sep))
        else:
            result[full_key] = value
    return result


def flatten_config(config: dict[str, Any], sep: str = ".") -> FlattenResult:
    """Flatten a nested config dict into dot-notation key-value pairs."""
    if not isinstance(config, dict):
        raise FlattenError(f"Config must be a dict, got {type(config).__name__}")

    original_keys = len(config)
    flat = _flatten(config, sep=sep)
    return FlattenResult(
        flat=flat,
        original_keys=original_keys,
        flat_keys=len(flat),
    )


def unflatten_config(flat: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Reconstruct a nested dict from dot-notation key-value pairs."""
    if not isinstance(flat, dict):
        raise FlattenError(f"Input must be a dict, got {type(flat).__name__}")

    result: dict[str, Any] = {}
    for key, value in flat.items():
        parts = key.split(sep)
        node = result
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = value
    return result
