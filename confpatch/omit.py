"""omit.py — Remove specific keys from a config by path."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class OmitError(Exception):
    pass


@dataclass
class OmitResult:
    removed: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)

    def has_changes(self) -> bool:
        return len(self.removed) > 0

    def count(self) -> int:
        return len(self.removed)

    def summary(self) -> str:
        if not self.removed:
            return "No keys omitted."
        keys = ", ".join(self.removed)
        return f"Omitted {len(self.removed)} key(s): {keys}"


def _get_parent(config: dict, parts: list[str]) -> tuple[dict, str]:
    """Walk to the parent dict and return (parent, final_key)."""
    node = config
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            raise OmitError(f"Key path not found: {'.'.join(parts)}")
        node = node[part]
    if not isinstance(node, dict):
        raise OmitError(f"Key path not found: {'.'.join(parts)}")
    return node, parts[-1]


def omit_keys(config: dict, keys: list[str], missing_ok: bool = False) -> OmitResult:
    """Remove keys (dot-notation supported) from a copy of config."""
    import copy

    if not isinstance(config, dict):
        raise OmitError("Config must be a dict.")

    result = copy.deepcopy(config)
    removed: list[str] = []

    for key in keys:
        parts = key.split(".")
        try:
            parent, leaf = _get_parent(result, parts)
        except OmitError:
            if missing_ok:
                continue
            raise

        if leaf not in parent:
            if missing_ok:
                continue
            raise OmitError(f"Key not found: {key}")

        del parent[leaf]
        removed.append(key)

    return OmitResult(removed=removed, config=result)
