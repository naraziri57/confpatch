"""Swap the values of two keys in a config dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SwapError(Exception):
    """Raised when a swap operation fails."""


@dataclass
class SwapResult:
    config: dict
    swapped: list[tuple[str, str]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.swapped) > 0

    def count(self) -> int:
        return len(self.swapped)

    def summary(self) -> str:
        if not self.swapped:
            return "No keys swapped."
        lines = [f"Swapped {self.count()} pair(s):"]
        for a, b in self.swapped:
            lines.append(f"  {a} <-> {b}")
        return "\n".join(lines)


def _get_nested(config: dict, key: str) -> Any:
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise SwapError(f"Key not found: {key!r}")
        node = node[part]
    return node


def _set_nested(config: dict, key: str, value: Any) -> dict:
    import copy
    result = copy.deepcopy(config)
    parts = key.split(".")
    node = result
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            raise SwapError(f"Intermediate key not found: {part!r} in {key!r}")
        node = node[part]
    node[parts[-1]] = value
    return result


def swap_keys(config: dict, pairs: list[tuple[str, str]]) -> SwapResult:
    """Swap the values of each (key_a, key_b) pair in config."""
    import copy
    result = copy.deepcopy(config)
    swapped: list[tuple[str, str]] = []

    for key_a, key_b in pairs:
        val_a = _get_nested(result, key_a)
        val_b = _get_nested(result, key_b)
        result = _set_nested(result, key_a, val_b)
        result = _set_nested(result, key_b, val_a)
        swapped.append((key_a, key_b))

    return SwapResult(config=result, swapped=swapped)
