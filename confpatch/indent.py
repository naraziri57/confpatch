"""Indent normalization for config values (string indentation detection and standardization)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class IndentError(Exception):
    """Raised when indent normalization fails."""


@dataclass
class IndentResult:
    original: dict
    normalized: dict
    changes: list[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.has_changes():
            return "No indentation changes."
        return f"Normalized indentation in {self.count()} value(s)."


def _normalize_string(value: str, indent: int, use_tabs: bool) -> str:
    """Re-indent a multiline string using the given indent size or tabs."""
    lines = value.splitlines()
    if len(lines) <= 1:
        return value
    unit = "\t" if use_tabs else " " * indent
    stripped = [lines[0]] + [unit + line.lstrip() for line in lines[1:]]
    return "\n".join(stripped)


def _normalize_value(value: Any, indent: int, use_tabs: bool, path: str, changes: list[str]) -> Any:
    if isinstance(value, dict):
        return {
            k: _normalize_value(v, indent, use_tabs, f"{path}.{k}" if path else k, changes)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [
            _normalize_value(item, indent, use_tabs, f"{path}[{i}]", changes)
            for i, item in enumerate(value)
        ]
    if isinstance(value, str) and "\n" in value:
        normalized = _normalize_string(value, indent, use_tabs)
        if normalized != value:
            changes.append(path)
        return normalized
    return value


def normalize_indent(config: dict, indent: int = 2, use_tabs: bool = False) -> IndentResult:
    """Normalize indentation of multiline string values in a config dict."""
    if not isinstance(config, dict):
        raise IndentError(f"Expected a dict, got {type(config).__name__}")
    if indent < 1:
        raise IndentError(f"indent must be >= 1, got {indent}")
    changes: list[str] = []
    normalized = _normalize_value(config, indent, use_tabs, "", changes)
    return IndentResult(original=config, normalized=normalized, changes=changes)
