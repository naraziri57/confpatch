"""Tests for confpatch.select."""

from __future__ import annotations

import pytest

from confpatch.select import SelectError, SelectResult, select_keys


@pytest.fixture
def config():
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "app": {
            "debug": True,
            "name": "myapp",
        },
        "version": "1.0",
    }


def test_select_top_level_key(config):
    result = select_keys(config, ["version"])
    assert result.selected == {"version": "1.0"}


def test_select_multiple_top_level_keys(config):
    result = select_keys(config, ["version", "app"])
    assert result.selected["version"] == "1.0"
    assert result.selected["app"] == {"debug": True, "name": "myapp"}


def test_select_dot_notation(config):
    result = select_keys(config, ["database.host"])
    assert result.selected == {"database": {"host": "localhost"}}


def test_select_multiple_dot_notation(config):
    result = select_keys(config, ["database.host", "database.port"])
    assert result.selected["database"]["host"] == "localhost"
    assert result.selected["database"]["port"] == 5432


def test_select_missing_key_non_strict(config):
    result = select_keys(config, ["version", "nonexistent"])
    assert "version" in result.selected
    assert "nonexistent" in result.missing


def test_select_missing_key_strict_raises(config):
    with pytest.raises(SelectError, match="nonexistent"):
        select_keys(config, ["nonexistent"], strict=True)


def test_select_does_not_mutate_original(config):
    original = dict(config)
    select_keys(config, ["version"])
    assert config == original


def test_select_not_a_dict_raises():
    with pytest.raises(SelectError, match="must be a dict"):
        select_keys(["not", "a", "dict"], ["key"])


def test_select_empty_keys_raises(config):
    with pytest.raises(SelectError, match="at least one key"):
        select_keys(config, [])


def test_select_result_has_data(config):
    result = select_keys(config, ["version"])
    assert result.has_data() is True


def test_select_result_count(config):
    result = select_keys(config, ["version", "app"])
    assert result.count() == 2


def test_select_result_summary_no_missing(config):
    result = select_keys(config, ["version"])
    assert "1 key" in result.summary()
    assert "not found" not in result.summary()


def test_select_result_summary_with_missing(config):
    result = select_keys(config, ["version", "ghost"])
    assert "not found" in result.summary()
    assert "ghost" in result.summary()


def test_select_all_missing_non_strict(config):
    result = select_keys(config, ["x", "y"])
    assert result.selected == {}
    assert result.has_data() is False
    assert set(result.missing) == {"x", "y"}
