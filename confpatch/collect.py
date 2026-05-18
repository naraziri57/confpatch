"""Collect specific keys from a config into a new flat or nested dict."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CollectError(Exception):
    pass


@dataclass
class CollectResult:
    collected: dict[str, Any]
    keys: list[str]
    missing: list[str] = field(default_factory=list)

    def has_data(self) -> bool:
        return bool(self.collected)

    def count(self) -> int:
        return len(self.collected)

    def summary(self) -> str:
        parts = [f"Collected {self.count()} key(s)"]
        if self.missing:
            parts.append(f"{len(self.missing)} missing: {', '.join(self.missing)}")
        return "; ".join(parts)


def _get_nested(config: dict, key: str) -> Any:
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(key)
        node = node[part]
    return node


def collect_keys(
    config: dict[str, Any],
    keys: list[str],
    skip_missing: bool = False,
) -> CollectResult:
    """Collect values for the given keys from config.

    Keys support dot notation. Returns a flat dict keyed by the original key string.
    """
    if not isinstance(config, dict):
        raise CollectError("config must be a dict")

    collected: dict[str, Any] = {}
    missing: list[str] = []

    for key in keys:
        try:
            collected[key] = _get_nested(config, key)
        except KeyError:
            if skip_missing:
                missing.append(key)
            else:
                raise CollectError(f"Key not found: {key!r}")

    return CollectResult(collected=collected, keys=keys, missing=missing)
