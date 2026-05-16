"""Reorder keys in a config dict according to a specified key order."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


class ReorderError(Exception):
    pass


@dataclass
class ReorderResult:
    original: dict[str, Any]
    reordered: dict[str, Any]
    moved: list[str]

    def has_changes(self) -> bool:
        return len(self.moved) > 0

    def count(self) -> int:
        return len(self.moved)

    def summary(self) -> str:
        if not self.has_changes():
            return "No keys reordered."
        return f"Reordered {self.count()} key(s): {', '.join(self.moved)}"


def reorder_keys(config: dict[str, Any], order: list[str], scope: str | None = None) -> ReorderResult:
    """Reorder top-level (or scoped) keys in config according to `order`.

    Keys not in `order` are appended after ordered keys in their original order.
    """
    if not isinstance(config, dict):
        raise ReorderError("Config must be a dict.")
    if not isinstance(order, list) or not all(isinstance(k, str) for k in order):
        raise ReorderError("Order must be a list of strings.")

    import copy
    result = copy.deepcopy(config)

    if scope:
        parts = scope.split(".")
        subtree = result
        for part in parts:
            if not isinstance(subtree, dict) or part not in subtree:
                raise ReorderError(f"Scope path '{scope}' not found in config.")
            subtree = subtree[part]
        if not isinstance(subtree, dict):
            raise ReorderError(f"Scope '{scope}' does not point to a dict.")
        reordered_sub, moved = _do_reorder(subtree, order)
        # write back
        target = result
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = reordered_sub
        return ReorderResult(original=config, reordered=result, moved=moved)

    reordered_top, moved = _do_reorder(result, order)
    return ReorderResult(original=config, reordered=reordered_top, moved=moved)


def _do_reorder(d: dict[str, Any], order: list[str]) -> tuple[dict[str, Any], list[str]]:
    ordered = {k: d[k] for k in order if k in d}
    rest = {k: v for k, v in d.items() if k not in ordered}
    moved = [k for k in order if k in d]
    return {**ordered, **rest}, moved
