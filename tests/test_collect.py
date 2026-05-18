"""Tests for confpatch.collect."""

from __future__ import annotations

import pytest

from confpatch.collect import CollectError, CollectResult, collect_keys


@pytest.fixture
def config():
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "app": {
            "name": "myapp",
            "debug": False,
        },
        "version": "1.0.0",
    }


def test_collect_top_level_key(config):
    result = collect_keys(config, ["version"])
    assert result.collected == {"version": "1.0.0"}


def test_collect_multiple_keys(config):
    result = collect_keys(config, ["version", "database"])
    assert result.collected["version"] == "1.0.0"
    assert result.collected["database"]["host"] == "localhost"


def test_collect_dot_notation(config):
    result = collect_keys(config, ["database.host", "database.port"])
    assert result.collected["database.host"] == "localhost"
    assert result.collected["database.port"] == 5432


def test_collect_missing_key_raises(config):
    with pytest.raises(CollectError, match="Key not found"):
        collect_keys(config, ["nonexistent"])


def test_collect_missing_key_skip(config):
    result = collect_keys(config, ["version", "missing"], skip_missing=True)
    assert "version" in result.collected
    assert "missing" not in result.collected
    assert "missing" in result.missing


def test_collect_does_not_mutate_original(config):
    original = dict(config)
    collect_keys(config, ["version"])
    assert config == original


def test_collect_not_dict_raises():
    with pytest.raises(CollectError, match="must be a dict"):
        collect_keys(["not", "a", "dict"], ["key"])


def test_collect_result_has_data(config):
    result = collect_keys(config, ["version"])
    assert result.has_data() is True


def test_collect_result_empty_when_all_missing(config):
    result = collect_keys(config, ["x", "y"], skip_missing=True)
    assert result.has_data() is False
    assert result.count() == 0


def test_collect_result_summary(config):
    result = collect_keys(config, ["version", "nope"], skip_missing=True)
    s = result.summary()
    assert "Collected" in s
    assert "missing" in s


def test_collect_result_summary_no_missing(config):
    result = collect_keys(config, ["version"])
    assert "missing" not in result.summary()


def test_collect_nested_missing_raises(config):
    with pytest.raises(CollectError, match="Key not found"):
        collect_keys(config, ["database.password"])


def test_collect_deeply_nested(config):
    cfg = {"a": {"b": {"c": 42}}}
    result = collect_keys(cfg, ["a.b.c"])
    assert result.collected["a.b.c"] == 42
