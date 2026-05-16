"""Tests for confpatch.cache module."""

import time
import pytest
from pathlib import Path

from confpatch.cache import (
    CacheEntry,
    CacheError,
    get_cached,
    set_cached,
    invalidate,
)


@pytest.fixture
def tmp_config(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    return f


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


def test_get_cached_miss_on_empty(tmp_config, cache_dir):
    result = get_cached(tmp_config, cache_dir=cache_dir)
    assert result is None


def test_set_and_get_cached(tmp_config, cache_dir):
    data = {"key": "value"}
    set_cached(tmp_config, data, cache_dir=cache_dir)
    result = get_cached(tmp_config, cache_dir=cache_dir)
    assert result == data


def test_get_cached_returns_none_if_file_missing(tmp_path, cache_dir):
    missing = tmp_path / "nonexistent.yaml"
    result = get_cached(missing, cache_dir=cache_dir)
    assert result is None


def test_set_cached_raises_if_file_missing(tmp_path, cache_dir):
    missing = tmp_path / "ghost.yaml"
    with pytest.raises(CacheError, match="File not found"):
        set_cached(missing, {"x": 1}, cache_dir=cache_dir)


def test_cache_invalidated_on_mtime_change(tmp_config, cache_dir):
    set_cached(tmp_config, {"key": "value"}, cache_dir=cache_dir)
    # Simulate file modification by touching with a future mtime
    new_mtime = tmp_config.stat().st_mtime + 5.0
    import os
    os.utime(tmp_config, (new_mtime, new_mtime))
    result = get_cached(tmp_config, cache_dir=cache_dir)
    assert result is None


def test_invalidate_removes_entry(tmp_config, cache_dir):
    set_cached(tmp_config, {"a": 1}, cache_dir=cache_dir)
    removed = invalidate(tmp_config, cache_dir=cache_dir)
    assert removed is True
    assert get_cached(tmp_config, cache_dir=cache_dir) is None


def test_invalidate_returns_false_if_not_cached(tmp_config, cache_dir):
    removed = invalidate(tmp_config, cache_dir=cache_dir)
    assert removed is False


def test_set_cached_returns_entry(tmp_config, cache_dir):
    entry = set_cached(tmp_config, {"z": 99}, cache_dir=cache_dir)
    assert isinstance(entry, CacheEntry)
    assert entry.data == {"z": 99}
    assert entry.mtime == tmp_config.stat().st_mtime


def test_cache_entry_roundtrip():
    entry = CacheEntry(key="abc", data={"x": 1}, mtime=1234.5, cached_at=9999.0)
    restored = CacheEntry.from_dict(entry.to_dict())
    assert restored.key == entry.key
    assert restored.data == entry.data
    assert restored.mtime == entry.mtime


def test_set_cached_overwrites_previous(tmp_config, cache_dir):
    set_cached(tmp_config, {"v": 1}, cache_dir=cache_dir)
    set_cached(tmp_config, {"v": 2}, cache_dir=cache_dir)
    result = get_cached(tmp_config, cache_dir=cache_dir)
    assert result == {"v": 2}
