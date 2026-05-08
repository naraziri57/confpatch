"""Compare two config files and report differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from confpatch.loaders import load_config
from confpatch.diff import compute_diff, format_diff


class CompareError(Exception):
    pass


@dataclass
class CompareResult:
    file_a: str
    file_b: str
    diff: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.diff)

    @property
    def change_count(self) -> int:
        return len(self.diff)

    def summary(self) -> str:
        if not self.has_differences:
            return f"No differences between '{self.file_a}' and '{self.file_b}'."
        return (
            f"Found {self.change_count} difference(s) between "
            f"'{self.file_a}' and '{self.file_b}'."
        )

    def format(self, color: bool = False) -> str:
        if not self.has_differences:
            return self.summary()
        return format_diff(self.diff, color=color)


def compare_configs(
    path_a: str | Path,
    path_b: str | Path,
    format_a: str | None = None,
    format_b: str | None = None,
) -> CompareResult:
    """Load two config files and return a CompareResult with their diff."""
    path_a = Path(path_a)
    path_b = Path(path_b)

    if not path_a.exists():
        raise CompareError(f"File not found: {path_a}")
    if not path_b.exists():
        raise CompareError(f"File not found: {path_b}")

    try:
        config_a = load_config(path_a, fmt=format_a)
    except Exception as exc:
        raise CompareError(f"Failed to load '{path_a}': {exc}") from exc

    try:
        config_b = load_config(path_b, fmt=format_b)
    except Exception as exc:
        raise CompareError(f"Failed to load '{path_b}': {exc}") from exc

    diff = compute_diff(config_a, config_b)
    return CompareResult(file_a=str(path_a), file_b=str(path_b), diff=diff)
