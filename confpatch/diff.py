"""Utilities for computing and displaying diffs between configs."""

from typing import Any


def compute_diff(original: dict, patched: dict, prefix: str = "") -> list[dict]:
    """Return a list of change records between two config dicts.

    Each record has keys: 'key', 'action', 'old', 'new'.
    Actions: 'added', 'removed', 'changed'.
    """
    changes = []
    all_keys = set(original) | set(patched)

    for key in sorted(all_keys):
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"

        if key not in original:
            changes.append({"key": full_key, "action": "added", "old": None, "new": patched[key]})
        elif key not in patched:
            changes.append({"key": full_key, "action": "removed", "old": original[key], "new": None})
        elif isinstance(original[key], dict) and isinstance(patched[key], dict):
            changes.extend(compute_diff(original[key], patched[key], prefix=full_key))
        elif original[key] != patched[key]:
            changes.append({
                "key": full_key,
                "action": "changed",
                "old": original[key],
                "new": patched[key],
            })

    return changes


def format_diff(changes: list[dict], color: bool = False) -> str:
    """Format a list of change records into a human-readable string."""
    if not changes:
        return "(no changes)"

    lines = []
    for change in changes:
        key = change["key"]
        action = change["action"]

        if action == "added":
            line = f"+ {key}: {change['new']!r}"
            lines.append(_colorize(line, "green") if color else line)
        elif action == "removed":
            line = f"- {key}: {change['old']!r}"
            lines.append(_colorize(line, "red") if color else line)
        elif action == "changed":
            line = f"~ {key}: {change['old']!r} -> {change['new']!r}"
            lines.append(_colorize(line, "yellow") if color else line)

    return "\n".join(lines)


def _colorize(text: str, color: str) -> str:
    codes = {"green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m"}
    reset = "\033[0m"
    return f"{codes.get(color, '')}{text}{reset}"
