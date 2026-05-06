"""Deep merge utilities for combining config dicts with patch dicts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class MergeError(Exception):
    """Raised when a merge operation fails due to type conflicts."""


MergeStrategy = str  # 'deep' | 'shallow' | 'replace'


def merge_configs(
    base: dict[str, Any],
    patch: dict[str, Any],
    strategy: MergeStrategy = "deep",
    overwrite_lists: bool = True,
) -> dict[str, Any]:
    """Return a new dict that is *base* merged with *patch*.

    Strategies:
        deep    – recursively merge nested dicts (default)
        shallow – only top-level keys are merged
        replace – patch entirely replaces base
    """
    if strategy not in ("deep", "shallow", "replace"):
        raise MergeError(f"Unknown merge strategy: {strategy!r}")

    if strategy == "replace":
        return deepcopy(patch)

    result = deepcopy(base)

    for key, patch_val in patch.items():
        if strategy == "deep" and key in result:
            base_val = result[key]
            if isinstance(base_val, dict) and isinstance(patch_val, dict):
                result[key] = merge_configs(base_val, patch_val, strategy="deep",
                                            overwrite_lists=overwrite_lists)
                continue
            if isinstance(base_val, list) and isinstance(patch_val, list) and not overwrite_lists:
                result[key] = base_val + patch_val
                continue
        result[key] = deepcopy(patch_val)

    return result


def merge_into(
    base: dict[str, Any],
    *patches: dict[str, Any],
    strategy: MergeStrategy = "deep",
    overwrite_lists: bool = True,
) -> dict[str, Any]:
    """Apply multiple patches to *base* in order, returning the final merged dict."""
    result = deepcopy(base)
    for patch in patches:
        result = merge_configs(result, patch, strategy=strategy,
                               overwrite_lists=overwrite_lists)
    return result
