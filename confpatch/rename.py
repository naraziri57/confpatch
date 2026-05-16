"""Rename keys in a config, supporting dot-notation paths."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class RenameError(Exception):
    """Raised when a rename operation fails."""


@dataclass
class RenameResult:
    renamed: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.renamed) > 0

    @property
    def count(self) -> int:
        return len(self.renamed)

    def summary(self) -> str:
        lines = [f"Renamed {self.count} key(s)."]
        for old, new in self.renamed:
            lines.append(f"  {old!r} -> {new!r}")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} missing key(s): {self.skipped}")
        return "\n".join(lines)


def _get_parent(config: dict, parts: list[str]) -> dict:
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise RenameError(f"Key path not found: {'.' .join(parts)}")
        node = node[part]
    return node  # type: ignore[return-value]


def rename_key(config: dict, old_path: str, new_name: str) -> dict:
    """Return a new config with old_path renamed to new_name at the same level."""
    import copy
    result = copy.deepcopy(config)
    parts = old_path.split(".")
    parent_parts, key = parts[:-1], parts[-1]

    parent: Any = result
    for part in parent_parts:
        if not isinstance(parent, dict) or part not in parent:
            raise RenameError(f"Parent path not found: {'.'.join(parent_parts)}")
        parent = parent[part]

    if not isinstance(parent, dict):
        raise RenameError(f"Parent of '{old_path}' is not a dict")
    if key not in parent:
        raise RenameError(f"Key '{old_path}' not found in config")
    if new_name in parent:
        raise RenameError(f"Target key '{new_name}' already exists at the same level")

    parent[new_name] = parent.pop(key)
    return result


def rename_keys(config: dict, renames: dict[str, str], skip_missing: bool = False) -> tuple[dict, RenameResult]:
    """Apply multiple renames. renames maps old_path -> new_name."""
    result = config
    report = RenameResult()
    for old_path, new_name in renames.items():
        try:
            result = rename_key(result, old_path, new_name)
            report.renamed.append((old_path, new_name))
        except RenameError:
            if skip_missing:
                report.skipped.append(old_path)
            else:
                raise
    return result, report
