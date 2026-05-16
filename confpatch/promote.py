"""Promote a nested config key to the top level."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


@dataclass
class PromoteResult:
    promoted: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    config: dict[str, Any] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return bool(self.promoted)

    def count(self) -> int:
        return len(self.promoted)

    def summary(self) -> str:
        if not self.has_changes():
            return "No keys promoted."
        keys = ", ".join(self.promoted.keys())
        return f"Promoted {self.count()} key(s) from '{self.source_path}': {keys}"


def _get_nested(config: dict, path: str) -> Any:
    parts = path.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise PromoteError(f"Key path '{path}' not found in config.")
        node = node[part]
    return node


def _del_nested(config: dict, path: str) -> dict:
    import copy
    result = copy.deepcopy(config)
    parts = path.split(".")
    node = result
    for part in parts[:-1]:
        node = node[part]
    del node[parts[-1]]
    return result


def promote_key(
    config: dict[str, Any],
    path: str,
    *,
    remove_source: bool = False,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote all keys from a nested dict at *path* to the top level."""
    subtree = _get_nested(config, path)
    if not isinstance(subtree, dict):
        raise PromoteError(
            f"Value at '{path}' is not a dict and cannot be promoted."
        )

    conflicts = [k for k in subtree if k in config and not overwrite]
    if conflicts:
        raise PromoteError(
            f"Keys already exist at top level (use overwrite=True): {conflicts}"
        )

    import copy
    result = copy.deepcopy(config)
    result.update(subtree)

    if remove_source:
        result = _del_nested(result, path)

    return PromoteResult(promoted=dict(subtree), source_path=path, config=result)
