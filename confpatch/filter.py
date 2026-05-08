"""Filter keys from a config or patch dict based on patterns or key lists."""

from __future__ import annotations

import fnmatch
from typing import Any


class FilterError(Exception):
    """Raised when filtering fails."""


def _matches_any(key: str, patterns: list[str]) -> bool:
    """Return True if key matches any glob pattern in patterns."""
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def filter_keys(
    data: dict[str, Any],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict[str, Any]:
    """Return a shallow-filtered copy of data.

    Args:
        data: The dict to filter.
        include: If given, only keys matching these glob patterns are kept.
        exclude: If given, keys matching these glob patterns are removed.

    Raises:
        FilterError: If data is not a dict or patterns are invalid.
    """
    if not isinstance(data, dict):
        raise FilterError(f"Expected a dict, got {type(data).__name__}")
    if include is not None and not isinstance(include, list):
        raise FilterError("include must be a list of strings")
    if exclude is not None and not isinstance(exclude, list):
        raise FilterError("exclude must be a list of strings")

    result = {}
    for key, value in data.items():
        str_key = str(key)
        if include is not None and not _matches_any(str_key, include):
            continue
        if exclude is not None and _matches_any(str_key, exclude):
            continue
        result[key] = value
    return result


def filter_patch(
    patch: dict[str, Any],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    recursive: bool = False,
) -> dict[str, Any]:
    """Filter a patch dict, optionally recursing into nested dicts.

    Args:
        patch: The patch dict to filter.
        include: Glob patterns for keys to include.
        exclude: Glob patterns for keys to exclude.
        recursive: If True, apply filtering recursively to nested dicts.

    Returns:
        Filtered patch dict.
    """
    filtered = filter_keys(patch, include=include, exclude=exclude)
    if recursive:
        for key, value in filtered.items():
            if isinstance(value, dict):
                filtered[key] = filter_patch(
                    value, include=include, exclude=exclude, recursive=True
                )
    return filtered
