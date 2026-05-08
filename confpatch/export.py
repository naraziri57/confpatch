"""Export config snapshots or patches to alternate formats (JSON, ENV)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ExportError(Exception):
    """Raised when export fails."""


def _flatten(data: dict, prefix: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dict into dot-separated keys."""
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten(value, full_key, sep))
        else:
            result[full_key] = value
    return result


def export_json(data: dict, dest: Path | str) -> Path:
    """Export config dict to a JSON file."""
    dest = Path(dest)
    try:
        dest.write_text(json.dumps(data, indent=2, default=str))
    except OSError as exc:
        raise ExportError(f"Failed to write JSON export: {exc}") from exc
    return dest


def export_env(data: dict, dest: Path | str, prefix: str = "") -> Path:
    """Export config dict to a .env-style file (KEY=value per line)."""
    dest = Path(dest)
    flat = _flatten(data)
    lines = []
    for key, value in sorted(flat.items()):
        env_key = key.upper().replace(".", "_").replace("-", "_")
        if prefix:
            env_key = f"{prefix.upper()}_{env_key}"
        lines.append(f"{env_key}={value}")
    try:
        dest.write_text(os.linesep.join(lines) + os.linesep)
    except OSError as exc:
        raise ExportError(f"Failed to write ENV export: {exc}") from exc
    return dest


def export_config(data: dict, dest: Path | str, fmt: str, prefix: str = "") -> Path:
    """Dispatch export based on format string ('json' or 'env')."""
    fmt = fmt.lower()
    if fmt == "json":
        return export_json(data, dest)
    elif fmt == "env":
        return export_env(data, dest, prefix=prefix)
    else:
        raise ExportError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'env'.")
