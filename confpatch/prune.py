"""Prune null/empty values from config or patch dicts."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


class PruneError(Exception):
    pass


@dataclass
class PruneResult:
    original: dict
    pruned: dict
    removed_keys: list[str]

    def has_removals(self) -> bool:
        return len(self.removed_keys) > 0

    def count(self) -> int:
        return len(self.removed_keys)

    def summary(self) -> str:
        if not self.has_removals():
            return "No keys pruned."
        keys = ", ".join(self.removed_keys)
        return f"Pruned {self.count()} key(s): {keys}"


def _prune(data: Any, prefix: str, removed: list[str], prune_empty: bool) -> Any:
    if not isinstance(data, dict):
        return data
    result = {}
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if v is None:
            removed.append(full_key)
            continue
        if prune_empty and v in ("", [], {}):
            removed.append(full_key)
            continue
        if isinstance(v, dict):
            nested = _prune(v, full_key, removed, prune_empty)
            if nested or not prune_empty:
                result[k] = nested
            else:
                removed.append(full_key)
        else:
            result[k] = v
    return result


def prune_config(config: dict, prune_empty: bool = False) -> PruneResult:
    """Remove null (and optionally empty) values from config dict."""
    if not isinstance(config, dict):
        raise PruneError("Config must be a dict.")
    removed: list[str] = []
    pruned = _prune(config, "", removed, prune_empty)
    return PruneResult(original=config, pruned=pruned, removed_keys=removed)
