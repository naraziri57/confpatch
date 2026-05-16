"""Index module: build and query a searchable index of config keys across files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from confpatch.loaders import load_config


class IndexError(Exception):
    pass


@dataclass
class IndexEntry:
    file: str
    key: str
    value: Any

    def to_dict(self) -> dict:
        return {"file": self.file, "key": self.key, "value": self.value}

    @staticmethod
    def from_dict(d: dict) -> "IndexEntry":
        return IndexEntry(file=d["file"], key=d["key"], value=d["value"])


def _flatten_keys(data: Any, prefix: str = "") -> dict[str, Any]:
    """Recursively flatten nested dict into dot-notation keys."""
    result = {}
    if isinstance(data, dict):
        for k, v in data.items():
            full_key = f"{prefix}.{k}" if prefix else k
            result.update(_flatten_keys(v, full_key))
    else:
        result[prefix] = data
    return result


def build_index(files: list[str | Path]) -> list[IndexEntry]:
    """Build an index of all keys across the given config files."""
    entries: list[IndexEntry] = []
    for f in files:
        path = Path(f)
        if not path.exists():
            raise IndexError(f"File not found: {path}")
        try:
            config = load_config(str(path))
        except Exception as e:
            raise IndexError(f"Failed to load {path}: {e}") from e
        flat = _flatten_keys(config)
        for key, value in flat.items():
            entries.append(IndexEntry(file=str(path), key=key, value=value))
    return entries


def search_index(entries: list[IndexEntry], query: str) -> list[IndexEntry]:
    """Return entries whose key contains the query string."""
    q = query.lower()
    return [e for e in entries if q in e.key.lower()]


def save_index(entries: list[IndexEntry], path: str | Path) -> None:
    """Persist index to a JSON file."""
    Path(path).write_text(json.dumps([e.to_dict() for e in entries], indent=2))


def load_index(path: str | Path) -> list[IndexEntry]:
    """Load index from a JSON file."""
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return [IndexEntry.from_dict(d) for d in data]
