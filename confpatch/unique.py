"""Enforce uniqueness constraints on list values in a config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class UniqueError(Exception):
    pass


@dataclass
class UniqueResult:
    original: dict
    result: dict
    deduped: dict[str, list]  # key -> list of removed duplicate values

    def has_changes(self) -> bool:
        return bool(self.deduped)

    def count(self) -> int:
        return sum(len(v) for v in self.deduped.values())

    def summary(self) -> str:
        if not self.has_changes():
            return "No duplicate list values found."
        lines = [f"Removed {self.count()} duplicate(s):"]
        for key, removed in self.deduped.items():
            lines.append(f"  {key}: removed {removed}")
        return "\n".join(lines)


def _dedupe_list(lst: list) -> tuple[list, list]:
    """Return (deduped_list, removed_items)."""
    seen: list = []
    removed: list = []
    for item in lst:
        # Use a simple equality check; unhashable types are handled gracefully
        if item not in seen:
            seen.append(item)
        else:
            removed.append(item)
    return seen, removed


def enforce_unique(
    config: dict,
    keys: list[str] | None = None,
    recursive: bool = True,
) -> UniqueResult:
    """Remove duplicate values from list fields in *config*.

    Args:
        config: The config dict to process.
        keys: If provided, only deduplicate these dot-notation keys.
        recursive: When *keys* is None, recurse into nested dicts.
    """
    if not isinstance(config, dict):
        raise UniqueError("Config must be a dict.")

    import copy
    result = copy.deepcopy(config)
    deduped: dict[str, list] = {}

    def _walk(node: Any, prefix: str) -> None:
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if keys is not None:
                if full_key not in keys:
                    if recursive:
                        _walk(v, full_key)
                    continue
            if isinstance(v, list):
                clean, removed = _dedupe_list(v)
                if removed:
                    node[k] = clean
                    deduped[full_key] = removed
            elif isinstance(v, dict) and recursive:
                _walk(v, full_key)

    _walk(result, "")
    return UniqueResult(original=config, result=result, deduped=deduped)
