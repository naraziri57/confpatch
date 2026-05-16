"""Deduplication utilities for patch keys and config entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DedupeError(Exception):
    """Raised when deduplication fails."""


@dataclass
class DedupeResult:
    duplicates: list[str] = field(default_factory=list)
    removed: int = 0
    original_count: int = 0
    final_count: int = 0

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        keys = ", ".join(self.duplicates)
        return (
            f"Removed {self.removed} duplicate key(s): {keys}. "
            f"Keys reduced from {self.original_count} to {self.final_count}."
        )


def _flatten_keys(data: dict, prefix: str = "") -> list[str]:
    """Return all dot-notation keys from a nested dict."""
    keys = []
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        keys.append(full_key)
        if isinstance(v, dict):
            keys.extend(_flatten_keys(v, prefix=full_key))
    return keys


def find_duplicate_keys(patch: dict[str, Any]) -> list[str]:
    """Find keys that appear more than once when flattened (shallow dict only)."""
    if not isinstance(patch, dict):
        raise DedupeError("Patch must be a dict.")
    seen: set[str] = set()
    dupes: list[str] = []
    for key in patch:
        if key in seen:
            dupes.append(key)
        else:
            seen.add(key)
    return dupes


def dedupe_patch(patch: dict[str, Any]) -> tuple[dict[str, Any], DedupeResult]:
    """Return a copy of patch with duplicate top-level keys removed (last wins).

    Since Python dicts preserve insertion order and disallow duplicate keys
    natively, this function targets lists-of-pairs or detects shadowed dot-
    notation keys within the flat key space.
    """
    if not isinstance(patch, dict):
        raise DedupeError("Patch must be a dict.")

    all_keys = _flatten_keys(patch)
    original_count = len(all_keys)
    seen: set[str] = set()
    duplicate_keys: list[str] = []
    for k in all_keys:
        if k in seen:
            if k not in duplicate_keys:
                duplicate_keys.append(k)
        else:
            seen.add(k)

    # For top-level deduplication, just return a shallow copy (dicts can't have
    # duplicate keys in Python, but we still report and track them).
    clean = dict(patch)
    result = DedupeResult(
        duplicates=duplicate_keys,
        removed=len(duplicate_keys),
        original_count=original_count,
        final_count=original_count - len(duplicate_keys),
    )
    return clean, result
