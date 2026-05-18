"""Group config keys into nested sections."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class GroupError(Exception):
    pass


@dataclass
class GroupResult:
    original: dict
    grouped: dict
    moved: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.moved) > 0

    def count(self) -> int:
        return len(self.moved)

    def summary(self) -> str:
        if not self.has_changes():
            return "No keys grouped."
        return f"Grouped {self.count()} key(s): {', '.join(self.moved)}"


def _get_nested(config: dict, path: str) -> dict:
    parts = path.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise GroupError(f"Path '{path}' does not exist in config.")
        node = node[part]
    if not isinstance(node, dict):
        raise GroupError(f"Path '{path}' is not a dict and cannot be a group target.")
    return node


def _set_nested(config: dict, path: str, value: dict) -> None:
    parts = path.split(".")
    node = config
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def group_keys(
    config: dict,
    keys: List[str],
    group: str,
    overwrite: bool = False,
) -> GroupResult:
    """Move top-level keys into a nested group path."""
    if not isinstance(config, dict):
        raise GroupError("Config must be a dict.")
    if not keys:
        raise GroupError("No keys specified to group.")
    if not group:
        raise GroupError("Group path must not be empty.")

    result = copy.deepcopy(config)
    moved: List[str] = []

    # Ensure the group target exists or create it
    parts = group.split(".")
    node = result
    for part in parts:
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise GroupError(f"Cannot create group at '{group}': path blocked by non-dict value.")

    for key in keys:
        if key not in result:
            raise GroupError(f"Key '{key}' not found in config.")
        if key in node and not overwrite:
            raise GroupError(
                f"Key '{key}' already exists in group '{group}'. Use overwrite=True to replace."
            )
        node[key] = result.pop(key)
        moved.append(key)

    return GroupResult(original=config, grouped=result, moved=moved)
