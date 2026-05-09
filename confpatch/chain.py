"""Apply multiple patch files in sequence to a config."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from confpatch.loaders import load_config, save_config
from confpatch.patch import load_patch, apply_patch


class ChainError(Exception):
    """Raised when a patch chain fails."""


@dataclass
class ChainResult:
    config_file: str
    patches_applied: list[str] = field(default_factory=list)
    patches_failed: list[tuple[str, str]] = field(default_factory=list)
    final_config: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return len(self.patches_failed) == 0

    def summary(self) -> str:
        applied = len(self.patches_applied)
        failed = len(self.patches_failed)
        return (
            f"Chain on '{self.config_file}': "
            f"{applied} applied, {failed} failed"
        )


def apply_chain(
    config_path: str | Path,
    patch_paths: list[str | Path],
    fmt: str | None = None,
    stop_on_error: bool = True,
    dry_run: bool = False,
) -> ChainResult:
    """Apply a sequence of patches to a config file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise ChainError(f"Config file not found: {config_path}")

    config, detected_fmt = load_config(str(config_path))
    resolved_fmt = fmt or detected_fmt
    result = ChainResult(config_file=str(config_path))
    current = dict(config)

    for patch_path in patch_paths:
        patch_path = Path(patch_path)
        try:
            patch = load_patch(str(patch_path))
            current = apply_patch(current, patch)
            result.patches_applied.append(str(patch_path))
        except Exception as exc:
            result.patches_failed.append((str(patch_path), str(exc)))
            if stop_on_error:
                break

    result.final_config = current

    if not dry_run and result.patches_applied:
        save_config(current, str(config_path), resolved_fmt)

    return result
