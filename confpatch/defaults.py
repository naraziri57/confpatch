"""Apply default values to config keys that are missing or null."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DefaultsError(Exception):
    pass


@dataclass
class DefaultsResult:
    applied: dict[str, Any] = field(default_factory=dict)
    skipped: dict[str, Any] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return bool(self.applied)

    def count(self) -> int:
        return len(self.applied)

    def summary(self) -> str:
        if not self.applied:
            return "No defaults applied."
        lines = [f"Applied {self.count()} default(s):"]
        for k, v in self.applied.items():
            lines.append(f"  {k} = {v!r}")
        return "\n".join(lines)


def _get_nested(config: dict, key: str) -> Any:
    """Retrieve a value using dot-notation key."""
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(key)
        node = node[part]
    return node


def _set_nested(config: dict, key: str, value: Any) -> dict:
    """Return a new config with the value set at the dot-notation key."""
    import copy
    result = copy.deepcopy(config)
    parts = key.split(".")
    node = result
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value
    return result


def apply_defaults(
    config: dict,
    defaults: dict[str, Any],
    overwrite_null: bool = True,
) -> tuple[dict, DefaultsResult]:
    """Apply defaults to config for keys that are absent or null.

    Args:
        config: The original config dict.
        defaults: Flat dot-notation key -> default value mapping.
        overwrite_null: If True, also replace None values with the default.

    Returns:
        (new_config, DefaultsResult)
    """
    if not isinstance(config, dict):
        raise DefaultsError("config must be a dict")
    if not isinstance(defaults, dict):
        raise DefaultsError("defaults must be a dict")

    result = DefaultsResult()
    current = config

    for key, default_value in defaults.items():
        try:
            existing = _get_nested(current, key)
            if overwrite_null and existing is None:
                current = _set_nested(current, key, default_value)
                result.applied[key] = default_value
            else:
                result.skipped[key] = existing
        except KeyError:
            current = _set_nested(current, key, default_value)
            result.applied[key] = default_value

    return current, result
