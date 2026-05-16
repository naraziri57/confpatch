"""Split a config file into multiple files by top-level keys."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from confpatch.loaders import load_config, save_config


class SplitError(Exception):
    """Raised when a split operation fails."""


@dataclass
class SplitResult:
    files_written: List[Path] = field(default_factory=list)
    keys_split: List[str] = field(default_factory=list)
    dry_run: bool = False

    def has_output(self) -> bool:
        return len(self.keys_split) > 0

    def count(self) -> int:
        return len(self.keys_split)

    def summary(self) -> str:
        if not self.has_output():
            return "No keys to split."
        mode = " (dry run)" if self.dry_run else ""
        return (
            f"Split {self.count()} key(s){mode}: "
            + ", ".join(self.keys_split)
        )


def split_config(
    config_path: str,
    output_dir: str,
    keys: Optional[List[str]] = None,
    fmt: Optional[str] = None,
    dry_run: bool = False,
) -> SplitResult:
    """Split top-level keys of a config into separate files.

    Args:
        config_path: Path to the source config file.
        output_dir: Directory where split files will be written.
        keys: Specific keys to split out. If None, all top-level keys are used.
        fmt: Output format ('yaml' or 'toml'). Inferred from source if not given.
        dry_run: If True, do not write any files.

    Returns:
        SplitResult describing what was (or would be) written.
    """
    src = Path(config_path)
    if not src.exists():
        raise SplitError(f"Config file not found: {config_path}")

    config = load_config(str(src))
    if not isinstance(config, dict):
        raise SplitError("Config must be a mapping at the top level.")

    inferred_fmt = fmt or ("toml" if src.suffix == ".toml" else "yaml")
    ext = ".toml" if inferred_fmt == "toml" else ".yaml"

    target_keys = keys if keys is not None else list(config.keys())
    missing = [k for k in target_keys if k not in config]
    if missing:
        raise SplitError(f"Keys not found in config: {missing}")

    out_dir = Path(output_dir)
    result = SplitResult(dry_run=dry_run)

    for key in target_keys:
        sub_config = {key: copy.deepcopy(config[key])}
        out_path = out_dir / f"{key}{ext}"
        if not dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            save_config(sub_config, str(out_path), fmt=inferred_fmt)
        result.files_written.append(out_path)
        result.keys_split.append(key)

    return result
