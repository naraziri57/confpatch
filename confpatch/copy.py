"""Copy keys within or between config sections."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CopyError(Exception):
    pass


@dataclass
class CopyResult:
    copied: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.copied) > 0

    def count(self) -> int:
        return len(self.copied)

    def summary(self) -> str:
        lines = [f"Copied {self.count()} key(s)."]
        for src, dst in self.copied:
            lines.append(f"  {src} -> {dst}")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} key(s) (already exist).")
        return "\n".join(lines)


def _get_nested(config: dict, key: str) -> Any:
    parts = key.split(".")
    node = config
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise CopyError(f"Source key not found: '{key}'")
        node = node[part]
    return node


def _set_nested(config: dict, key: str, value: Any, overwrite: bool) -> bool:
    """Returns True if the key was set, False if skipped."""
    parts = key.split(".")
    node = config
    for part in parts[:-1]:
        if part not in node:
            node[part] = {}
        elif not isinstance(node[part], dict):
            raise CopyError(f"Cannot traverse into non-dict at '{part}'")
        node = node[part]
    leaf = parts[-1]
    if leaf in node and not overwrite:
        return False
    node[leaf] = value
    return True


def copy_key(
    config: dict,
    src: str,
    dst: str,
    overwrite: bool = False,
) -> tuple[dict, CopyResult]:
    """Copy a single key from src to dst within the config."""
    import copy
    result = config
    result = copy.deepcopy(config)
    value = _get_nested(result, src)
    was_set = _set_nested(result, dst, value, overwrite)
    report = CopyResult()
    if was_set:
        report.copied.append((src, dst))
    else:
        report.skipped.append((src, dst))
    return result, report


def copy_keys(
    config: dict,
    pairs: list[tuple[str, str]],
    overwrite: bool = False,
) -> tuple[dict, CopyResult]:
    """Copy multiple key pairs within the config."""
    import copy
    result = copy.deepcopy(config)
    report = CopyResult()
    for src, dst in pairs:
        value = _get_nested(result, src)
        was_set = _set_nested(result, dst, value, overwrite)
        if was_set:
            report.copied.append((src, dst))
        else:
            report.skipped.append((src, dst))
    return result, report
