"""Select specific keys from a config and produce a new config subset."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SelectError(Exception):
    pass


@dataclass
class SelectResult:
    selected: dict[str, Any]
    keys: list[str]
    missing: list[str] = field(default_factory=list)

    def has_data(self) -> bool:
        return bool(self.selected)

    def count(self) -> int:
        return len(self.selected)

    def summary(self) -> str:
        parts = [f"Selected {self.count()} key(s)"]
        if self.missing:
            parts.append(f"{len(self.missing)} not found: {', '.join(self.missing)}")
        return "; ".join(parts)


def _get_nested(config: dict, key: str) -> Any:
    """Resolve a dot-notation key from config."""
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(key)
        node = node[part]
    return node


def _set_nested(result: dict, key: str, value: Any) -> None:
    """Set a dot-notation key in result dict, creating intermediate dicts."""
    parts = key.split(".")
    node = result
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def select_keys(
    config: dict[str, Any],
    keys: list[str],
    strict: bool = False,
) -> SelectResult:
    """Extract a subset of keys from config into a new dict.

    Args:
        config: Source configuration dict.
        keys: List of dot-notation keys to select.
        strict: If True, raise SelectError on missing keys.

    Returns:
        SelectResult with the new subset dict.
    """
    if not isinstance(config, dict):
        raise SelectError("config must be a dict")
    if not keys:
        raise SelectError("at least one key must be specified")

    selected: dict[str, Any] = {}
    missing: list[str] = []

    for key in keys:
        try:
            value = _get_nested(config, key)
            _set_nested(selected, key, value)
        except KeyError:
            if strict:
                raise SelectError(f"Key not found: {key!r}")
            missing.append(key)

    return SelectResult(selected=selected, keys=keys, missing=missing)
