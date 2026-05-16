"""Scope support: restrict patch application to a subtree of the config."""

from __future__ import annotations

from typing import Any


class ScopeError(Exception):
    """Raised when a scope operation fails."""


def _get_subtree(config: dict, scope: str) -> dict:
    """Return the nested dict located at *scope* (dot-separated path)."""
    parts = scope.split(".")
    node: Any = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise ScopeError(f"Scope path '{scope}' not found in config")
        node = node[part]
    if not isinstance(node, dict):
        raise ScopeError(
            f"Scope target '{scope}' is not a dict (got {type(node).__name__})"
        )
    return node


def _set_subtree(config: dict, scope: str, subtree: dict) -> dict:
    """Return a shallow-copied config with *subtree* written back at *scope*."""
    import copy

    result = copy.deepcopy(config)
    parts = scope.split(".")
    node = result
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = subtree
    return result


def apply_scoped_patch(config: dict, patch: dict, scope: str) -> dict:
    """Apply *patch* only within the subtree identified by *scope*.

    Returns a new config dict with the patch applied inside the scope.
    The rest of the config is left untouched.
    """
    import copy
    from confpatch.patch import apply_patch

    subtree = _get_subtree(config, scope)
    patched_subtree = apply_patch(subtree, patch)
    return _set_subtree(config, scope, patched_subtree)


def extract_scope(config: dict, scope: str) -> dict:
    """Return a copy of the subtree at *scope*."""
    import copy

    return copy.deepcopy(_get_subtree(config, scope))
