"""Simple file-based cache for parsed config/patch results."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


class CacheError(Exception):
    pass


@dataclass
class CacheEntry:
    key: str
    data: Any
    mtime: float
    cached_at: float

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "data": self.data,
            "mtime": self.mtime,
            "cached_at": self.cached_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CacheEntry":
        return cls(
            key=d["key"],
            data=d["data"],
            mtime=d["mtime"],
            cached_at=d["cached_at"],
        )


def _cache_path(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "confpatch_cache.json"


def _file_key(filepath: Path) -> str:
    return hashlib.md5(str(filepath.resolve()).encode()).hexdigest()


def _load_cache(cache_dir: Path) -> dict:
    path = _cache_path(cache_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_cache(cache_dir: Path, data: dict) -> None:
    _cache_path(cache_dir).write_text(json.dumps(data, indent=2))


def get_cached(filepath: Path, cache_dir: Optional[Path] = None) -> Optional[Any]:
    """Return cached data for filepath if still valid (mtime unchanged)."""
    if cache_dir is None:
        cache_dir = Path(os.path.expanduser("~/.cache/confpatch"))
    if not filepath.exists():
        return None
    current_mtime = filepath.stat().st_mtime
    raw = _load_cache(cache_dir)
    key = _file_key(filepath)
    entry_data = raw.get(key)
    if entry_data is None:
        return None
    entry = CacheEntry.from_dict(entry_data)
    if entry.mtime != current_mtime:
        return None
    return entry.data


def set_cached(filepath: Path, data: Any, cache_dir: Optional[Path] = None) -> CacheEntry:
    """Store data in cache keyed by filepath and its current mtime."""
    if cache_dir is None:
        cache_dir = Path(os.path.expanduser("~/.cache/confpatch"))
    if not filepath.exists():
        raise CacheError(f"File not found: {filepath}")
    mtime = filepath.stat().st_mtime
    key = _file_key(filepath)
    entry = CacheEntry(key=key, data=data, mtime=mtime, cached_at=time.time())
    raw = _load_cache(cache_dir)
    raw[key] = entry.to_dict()
    _save_cache(cache_dir, raw)
    return entry


def invalidate(filepath: Path, cache_dir: Optional[Path] = None) -> bool:
    """Remove cache entry for filepath. Returns True if entry existed."""
    if cache_dir is None:
        cache_dir = Path(os.path.expanduser("~/.cache/confpatch"))
    key = _file_key(filepath)
    raw = _load_cache(cache_dir)
    if key in raw:
        del raw[key]
        _save_cache(cache_dir, raw)
        return True
    return False
