"""Generate apply reports summarising what confpatch changed."""

from dataclasses import dataclass, field
from typing import Any

from confpatch.diff import compute_diff, format_diff


@dataclass
class ApplyReport:
    """Holds the result of a patch apply operation."""

    source_file: str
    patch_file: str
    original: dict
    patched: dict
    changes: list[dict] = field(init=False)

    def __post_init__(self) -> None:
        self.changes = compute_diff(self.original, self.patched)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def summary(self, color: bool = False) -> str:
        """Return a formatted summary string for the apply operation."""
        lines = [
            f"confpatch apply report",
            f"  source : {self.source_file}",
            f"  patch  : {self.patch_file}",
            f"  changes: {self.change_count}",
            "",
            format_diff(self.changes, color=color),
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialisable representation of the report."""
        return {
            "source_file": self.source_file,
            "patch_file": self.patch_file,
            "change_count": self.change_count,
            "changes": self.changes,
        }
