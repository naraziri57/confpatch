"""Tests for confpatch.summarize."""
from __future__ import annotations

import pytest

from confpatch.summarize import SummarizeError, SummarizeResult, summarize_config


# ---------------------------------------------------------------------------
# summarize_config
# ---------------------------------------------------------------------------

def test_summarize_flat_config():
    config = {"host": "localhost", "port": 8080, "debug": True}
    result = summarize_config(config)
    assert isinstance(result, SummarizeResult)
    assert set(result.top_level_keys) == {"host", "port", "debug"}
    assert result.total_keys == 3
    assert result.max_depth == 1


def test_summarize_nested_config():
    config = {"db": {"host": "localhost", "port": 5432}, "app": {"name": "test"}}
    result = summarize_config(config)
    assert result.total_keys == 5  # db, host, port, app, name — wait: top walk adds db/app then their children
    assert result.max_depth >= 2


def test_summarize_top_level_keys_order():
    config = {"z": 1, "a": 2, "m": 3}
    result = summarize_config(config)
    assert result.top_level_keys == ["z", "a", "m"]


def test_summarize_type_counts_basic():
    config = {"name": "alice", "age": 30, "active": True}
    result = summarize_config(config)
    assert result.type_counts.get("str", 0) >= 1
    assert result.type_counts.get("int", 0) >= 1
    assert result.type_counts.get("bool", 0) >= 1


def test_summarize_empty_dict():
    result = summarize_config({})
    assert result.top_level_keys == []
    assert result.total_keys == 0
    assert result.max_depth == 0


def test_summarize_non_dict_raises():
    with pytest.raises(SummarizeError):
        summarize_config(["a", "b"])


def test_summarize_none_raises():
    with pytest.raises(SummarizeError):
        summarize_config(None)  # type: ignore[arg-type]


def test_summarize_deep_nesting():
    config = {"a": {"b": {"c": {"d": "value"}}}}
    result = summarize_config(config)
    assert result.max_depth >= 4


def test_summarize_with_list_values():
    config = {"items": [1, 2, 3], "name": "test"}
    result = summarize_config(config)
    assert result.total_keys >= 2


# ---------------------------------------------------------------------------
# SummarizeResult.summary
# ---------------------------------------------------------------------------

def test_summary_string_contains_key_count():
    result = SummarizeResult(
        top_level_keys=["a", "b"],
        total_keys=5,
        max_depth=3,
        type_counts={"str": 3, "int": 2},
    )
    s = result.summary()
    assert "5" in s
    assert "3" in s
    assert "str" in s
    assert "int" in s


def test_summary_empty_result():
    result = SummarizeResult()
    s = result.summary()
    assert "0" in s
