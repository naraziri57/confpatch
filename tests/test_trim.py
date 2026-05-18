"""Tests for confpatch.trim."""

import pytest

from confpatch.trim import TrimError, TrimResult, trim_config


def test_trim_no_changes_on_clean_config():
    config = {"host": "localhost", "port": 8080}
    result = trim_config(config)
    assert not result.has_changes()
    assert result.trimmed == config


def test_trim_strips_leading_whitespace():
    config = {"host": "  localhost"}
    result = trim_config(config)
    assert result.trimmed["host"] == "localhost"
    assert result.has_changes()
    assert "host" in result.changed_keys


def test_trim_strips_trailing_whitespace():
    config = {"name": "myapp   "}
    result = trim_config(config)
    assert result.trimmed["name"] == "myapp"
    assert result.has_changes()


def test_trim_strips_both_sides():
    config = {"key": "  value  "}
    result = trim_config(config)
    assert result.trimmed["key"] == "value"


def test_trim_non_string_passthrough():
    config = {"count": 42, "flag": True, "ratio": 3.14}
    result = trim_config(config)
    assert result.trimmed == config
    assert not result.has_changes()


def test_trim_nested_dict():
    config = {"db": {"host": "  db.local ", "port": 5432}}
    result = trim_config(config)
    assert result.trimmed["db"]["host"] == "db.local"
    assert "db.host" in result.changed_keys


def test_trim_does_not_mutate_original():
    config = {"key": "  hello  "}
    original_value = config["key"]
    trim_config(config)
    assert config["key"] == original_value


def test_trim_count():
    config = {"a": " x ", "b": " y ", "c": "clean"}
    result = trim_config(config)
    assert result.count() == 2


def test_trim_summary_with_changes():
    config = {"key": " val "}
    result = trim_config(config)
    summary = result.summary()
    assert "1" in summary
    assert "key" in summary


def test_trim_summary_no_changes():
    config = {"key": "val"}
    result = trim_config(config)
    assert result.summary() == "No values trimmed."


def test_trim_not_a_dict_raises():
    with pytest.raises(TrimError):
        trim_config(["not", "a", "dict"])  # type: ignore


def test_trim_empty_string_unchanged():
    config = {"empty": ""}
    result = trim_config(config)
    assert result.trimmed["empty"] == ""
    assert not result.has_changes()


def test_trim_whitespace_only_becomes_empty():
    config = {"blank": "   "}
    result = trim_config(config)
    assert result.trimmed["blank"] == ""
    assert result.has_changes()
