"""String interpolation across config values using references to other keys."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

REF_PATTERN = re.compile(r"\$\{([^}]+)\}")


class InterpolateError(Exception):
    pass


@dataclass
class InterpolateResult:
    original: dict
    result: dict
    resolved: list[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.resolved) > 0

    def count(self) -> int:
        return len(self.resolved)

    def summary(self) -> str:
        if not self.resolved:
            return "No interpolations resolved."
        keys = ", ".join(self.resolved)
        return f"Resolved {self.count()} interpolation(s): {keys}"


def _get_nested(config: dict, dotted_key: str) -> Any:
    parts = dotted_key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise InterpolateError(f"Reference key not found: '{dotted_key}'")
        node = node[part]
    return node


def _interpolate_string(value: str, config: dict) -> tuple[str, list[str]]:
    resolved = []

    def replace(match: re.Match) -> str:
        ref_key = match.group(1)
        ref_value = _get_nested(config, ref_key)
        resolved.append(ref_key)
        return str(ref_value)

    result = REF_PATTERN.sub(replace, value)
    return result, resolved


def _walk(node: Any, config: dict, path: str = "") -> tuple[Any, list[str]]:
    all_resolved: list[str] = []
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            child_path = f"{path}.{k}" if path else k
            new_v, resolved = _walk(v, config, child_path)
            out[k] = new_v
            all_resolved.extend(resolved)
        return out, all_resolved
    elif isinstance(node, list):
        out_list = []
        for i, item in enumerate(node):
            new_item, resolved = _walk(item, config, f"{path}[{i}]")
            out_list.append(new_item)
            all_resolved.extend(resolved)
        return out_list, all_resolved
    elif isinstance(node, str) and REF_PATTERN.search(node):
        new_val, resolved = _interpolate_string(node, config)
        return new_val, resolved
    return node, []


def interpolate_config(config: dict) -> InterpolateResult:
    """Resolve ${key.path} references within a config dict."""
    if not isinstance(config, dict):
        raise InterpolateError("Config must be a dict.")
    result, resolved = _walk(config, config)
    return InterpolateResult(original=config, result=result, resolved=resolved)
