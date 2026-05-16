"""Tests for confpatch.extract."""

from __future__ import annotations

import pytest
import yaml

from confpatch.extract import (
    ExtractError,
    ExtractResult,
    _get_nested,
    extract_keys,
    extract_from_file,
)


# --- _get_nested ---

def test_get_nested_top_level():
    assert _get_nested({"a": 1}, "a") == 1


def test_get_nested_dot_notation():
    assert _get_nested({"a": {"b": 42}}, "a.b") == 42


def test_get_nested_deep():
    cfg = {"x": {"y": {"z": "deep"}}}
    assert _get_nested(cfg, "x.y.z") == "deep"


def test_get_nested_missing_raises():
    with pytest.raises(ExtractError, match="Key not found"):
        _get_nested({"a": 1}, "b")


def test_get_nested_missing_nested_raises():
    with pytest.raises(ExtractError, match="Key not found"):
        _get_nested({"a": {"b": 1}}, "a.c")


# --- extract_keys ---

def test_extract_keys_single():
    result = extract_keys({"a": 1, "b": 2}, ["a"])
    assert result == {"a": 1}


def test_extract_keys_multiple():
    result = extract_keys({"a": 1, "b": 2, "c": 3}, ["a", "c"])
    assert result == {"a": 1, "c": 3}


def test_extract_keys_dot_notation():
    cfg = {"db": {"host": "localhost", "port": 5432}}
    result = extract_keys(cfg, ["db.host"])
    assert result == {"db.host": "localhost"}


def test_extract_keys_not_dict_raises():
    with pytest.raises(ExtractError, match="Config must be a dict"):
        extract_keys(["a", "b"], ["a"])


def test_extract_keys_missing_key_raises():
    with pytest.raises(ExtractError):
        extract_keys({"a": 1}, ["z"])


# --- ExtractResult ---

def test_extract_result_has_data_true():
    r = ExtractResult(source="f.yaml", keys=["a"], extracted={"a": 1})
    assert r.has_data() is True


def test_extract_result_has_data_false():
    r = ExtractResult(source="f.yaml", keys=[], extracted={})
    assert r.has_data() is False


def test_extract_result_count():
    r = ExtractResult(source="f.yaml", keys=["a", "b"], extracted={"a": 1, "b": 2})
    assert r.count() == 2


def test_extract_result_summary_with_data():
    r = ExtractResult(source="f.yaml", keys=["a"], extracted={"a": 1})
    assert "Extracted 1" in r.summary()
    assert "f.yaml" in r.summary()


def test_extract_result_summary_empty():
    r = ExtractResult(source="f.yaml", keys=[], extracted={})
    assert "No keys" in r.summary()


# --- extract_from_file ---

def test_extract_from_file_basic(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"name": "alice", "age": 30}))
    result = extract_from_file(str(cfg), ["name"])
    assert result.extracted == {"name": "alice"}


def test_extract_from_file_writes_dest(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"x": 10, "y": 20}))
    dest = tmp_path / "out.yaml"
    extract_from_file(str(cfg), ["x"], dest=str(dest))
    data = yaml.safe_load(dest.read_text())
    assert data == {"x": 10}


def test_extract_from_file_dry_run_no_write(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"x": 10}))
    dest = tmp_path / "out.yaml"
    extract_from_file(str(cfg), ["x"], dest=str(dest), dry_run=True)
    assert not dest.exists()


def test_extract_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_from_file("/nonexistent/config.yaml", ["key"])
