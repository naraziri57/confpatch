"""Summarize a config file: key count, depth, types, and top-level keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SummarizeError(Exception):
    pass


@dataclass
class SummarizeResult:
    top_level_keys: list[str] = field(default_factory=list)
    total_keys: int = 0
    max_depth: int = 0
    type_counts: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        types = ", ".join(f"{t}={n}" for t, n in sorted(self.type_counts.items()))
        return (
            f"{self.total_keys} keys, max depth {self.max_depth}, "
            f"top-level: {len(self.top_level_keys)}, types: [{types}]"
        )


def _walk(obj: Any, depth: int) -> tuple[int, int, dict[str, int]]:
    """Return (total_keys, max_depth, type_counts) for obj."""
    type_counts: dict[str, int] = {}
    total = 0
    max_d = depth

    if isinstance(obj, dict):
        for v in obj.values():
            total += 1
            t = type(v).__name__
            type_counts[t] = type_counts.get(t, 0) + 1
            sub_total, sub_depth, sub_types = _walk(v, depth + 1)
            total += sub_total
            max_d = max(max_d, sub_depth)
            for st, sn in sub_types.items():
                type_counts[st] = type_counts.get(st, 0) + sn
    elif isinstance(obj, list):
        for item in obj:
            sub_total, sub_depth, sub_types = _walk(item, depth)
            total += sub_total
            max_d = max(max_d, sub_depth)
            for st, sn in sub_types.items():
                type_counts[st] = type_counts.get(st, 0) + sn

    return total, max_d, type_counts


def summarize_config(config: Any) -> SummarizeResult:
    """Produce a SummarizeResult for the given config dict."""
    if not isinstance(config, dict):
        raise SummarizeError(f"Expected a dict, got {type(config).__name__}")

    top_level_keys = list(config.keys())
    total, max_depth, type_counts = _walk(config, 1)

    return SummarizeResult(
        top_level_keys=top_level_keys,
        total_keys=total,
        max_depth=max_depth,
        type_counts=type_counts,
    )
