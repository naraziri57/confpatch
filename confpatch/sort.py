"""Sort keys in a config dict alphabetically or by custom order."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class SortError(Exception):
    pass


@dataclass
class SortResult:
    original: dict
    sorted_config: dict
    changed_keys: list[str]

    def has_changes(self) -> bool:
        return bool(self.changed_keys)

    def count(self) -> int:
        return len(self.changed_keys)

    def summary(self) -> str:
        if not self.has_changes():
            return "No keys reordered."
        return f"Reordered {self.count()} key(s) by sort."


def _sort_dict(data: Any, recursive: bool, reverse: bool) -> Any:
    if not isinstance(data, dict):
        return data
    sorted_keys = sorted(data.keys(), reverse=reverse)
    result = {}
    for k in sorted_keys:
        v = data[k]
        result[k] = _sort_dict(v, recursive, reverse) if recursive else v
    return result


def _changed_keys(original: dict, sorted_cfg: dict, prefix: str = "") -> list[str]:
    """Return dot-paths of keys whose position changed relative to original."""
    orig_order = list(original.keys())
    new_order = list(sorted_cfg.keys())
    changed = []
    for i, key in enumerate(new_order):
        path = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if orig_order[i] != new_order[i]:
            changed.append(path)
        if isinstance(original.get(key), dict) and isinstance(sorted_cfg.get(key), dict):
            changed.extend(_changed_keys(original[key], sorted_cfg[key], prefix=path))
    return list(dict.fromkeys(changed))  # dedupe, preserve order


def sort_config(
    config: dict,
    recursive: bool = True,
    reverse: bool = False,
) -> SortResult:
    """Sort all keys in a config dict alphabetically.

    Args:
        config: The source config dict.
        recursive: If True, sort nested dicts as well.
        reverse: If True, sort in descending order.

    Returns:
        SortResult with the sorted config and metadata.
    """
    if not isinstance(config, dict):
        raise SortError(f"Expected a dict, got {type(config).__name__}")

    sorted_cfg = _sort_dict(config, recursive=recursive, reverse=reverse)
    changed = _changed_keys(config, sorted_cfg)
    return SortResult(original=config, sorted_config=sorted_cfg, changed_keys=changed)
