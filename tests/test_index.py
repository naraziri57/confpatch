"""Tests for confpatch.index."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from confpatch.index import (
    IndexEntry,
    IndexError,
    _flatten_keys,
    build_index,
    load_index,
    save_index,
    search_index,
)


@pytest.fixture
def yaml_config(tmp_path: Path) -> Path:
    p = tmp_path / "config.yaml"
    p.write_text("database:\n  host: localhost\n  port: 5432\napp:\n  debug: true\n")
    return p


def test_flatten_keys_simple():
    data = {"a": 1, "b": 2}
    assert _flatten_keys(data) == {"a": 1, "b": 2}


def test_flatten_keys_nested():
    data = {"db": {"host": "localhost", "port": 5432}}
    result = _flatten_keys(data)
    assert result == {"db.host": "localhost", "db.port": 5432}


def test_flatten_keys_deep():
    data = {"a": {"b": {"c": 42}}}
    assert _flatten_keys(data) == {"a.b.c": 42}


def test_flatten_keys_scalar():
    assert _flatten_keys("hello", prefix="x") == {"x": "hello"}


def test_build_index_returns_entries(yaml_config: Path):
    entries = build_index([yaml_config])
    keys = [e.key for e in entries]
    assert "database.host" in keys
    assert "database.port" in keys
    assert "app.debug" in keys


def test_build_index_entry_values(yaml_config: Path):
    entries = build_index([yaml_config])
    host_entry = next(e for e in entries if e.key == "database.host")
    assert host_entry.value == "localhost"
    assert host_entry.file == str(yaml_config)


def test_build_index_file_not_found(tmp_path: Path):
    with pytest.raises(IndexError, match="File not found"):
        build_index([tmp_path / "missing.yaml"])


def test_build_index_multiple_files(tmp_path: Path):
    f1 = tmp_path / "a.yaml"
    f2 = tmp_path / "b.yaml"
    f1.write_text("x: 1\n")
    f2.write_text("y: 2\n")
    entries = build_index([f1, f2])
    assert any(e.key == "x" for e in entries)
    assert any(e.key == "y" for e in entries)


def test_search_index_finds_match(yaml_config: Path):
    entries = build_index([yaml_config])
    results = search_index(entries, "host")
    assert len(results) == 1
    assert results[0].key == "database.host"


def test_search_index_case_insensitive(yaml_config: Path):
    entries = build_index([yaml_config])
    results = search_index(entries, "HOST")
    assert len(results) == 1


def test_search_index_no_match(yaml_config: Path):
    entries = build_index([yaml_config])
    results = search_index(entries, "nonexistent")
    assert results == []


def test_save_and_load_index(tmp_path: Path, yaml_config: Path):
    entries = build_index([yaml_config])
    index_file = tmp_path / "index.json"
    save_index(entries, index_file)
    loaded = load_index(index_file)
    assert len(loaded) == len(entries)
    assert loaded[0].key == entries[0].key


def test_load_index_empty(tmp_path: Path):
    result = load_index(tmp_path / "nonexistent.json")
    assert result == []


def test_index_entry_to_dict():
    e = IndexEntry(file="f.yaml", key="a.b", value=42)
    assert e.to_dict() == {"file": "f.yaml", "key": "a.b", "value": 42}


def test_index_entry_from_dict():
    d = {"file": "f.yaml", "key": "a.b", "value": 42}
    e = IndexEntry.from_dict(d)
    assert e.file == "f.yaml"
    assert e.key == "a.b"
    assert e.value == 42
