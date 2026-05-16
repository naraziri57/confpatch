"""Tests for confpatch.truncate."""

import pytest

from confpatch.truncate import (
    TruncateError,
    TruncateResult,
    truncate_config,
    _truncate_value,
)


def test_truncate_value_short_string_unchanged():
    val, changed = _truncate_value("hello", 10, "...")
    assert val == "hello"
    assert changed is False


def test_truncate_value_long_string_truncated():
    val, changed = _truncate_value("hello world", 5, "...")
    assert val == "hello..."
    assert changed is True


def test_truncate_value_non_string_passthrough():
    val, changed = _truncate_value(42, 5, "...")
    assert val == 42
    assert changed is False


def test_truncate_config_no_long_values():
    config = {"host": "localhost", "port": 8080}
    out, result = truncate_config(config, max_length=50)
    assert out == config
    assert not result.has_truncations
    assert result.count == 0


def test_truncate_config_single_long_value():
    config = {"description": "a" * 200}
    out, result = truncate_config(config, max_length=10)
    assert out["description"] == "a" * 10 + "..."
    assert result.has_truncations
    assert result.count == 1
    assert "description" in result.truncated_keys
    assert result.original_lengths["description"] == 200


def test_truncate_config_nested():
    config = {"db": {"password": "s" * 100, "host": "localhost"}}
    out, result = truncate_config(config, max_length=20)
    assert out["db"]["host"] == "localhost"
    assert out["db"]["password"] == "s" * 20 + "..."
    assert result.count == 1
    assert any("password" in k for k in result.truncated_keys)


def test_truncate_config_does_not_mutate_original():
    config = {"msg": "x" * 50}
    original_val = config["msg"]
    truncate_config(config, max_length=10)
    assert config["msg"] == original_val


def test_truncate_config_custom_suffix():
    config = {"note": "hello world"}
    out, result = truncate_config(config, max_length=5, suffix="~~")
    assert out["note"] == "hello~~"


def test_truncate_config_not_a_dict_raises():
    with pytest.raises(TruncateError, match="config must be a dict"):
        truncate_config(["not", "a", "dict"])


def test_truncate_config_invalid_max_length_raises():
    with pytest.raises(TruncateError, match="max_length must be at least 1"):
        truncate_config({"key": "value"}, max_length=0)


def test_truncate_result_summary_no_truncations():
    result = TruncateResult()
    assert "No values truncated" in result.summary()


def test_truncate_result_summary_with_truncations():
    result = TruncateResult(
        truncated_keys=["foo.bar"],
        original_lengths={"foo.bar": 150},
    )
    summary = result.summary()
    assert "foo.bar" in summary
    assert "150" in summary


def test_truncate_config_multiple_keys():
    config = {"a": "x" * 30, "b": "y" * 30, "c": "short"}
    out, result = truncate_config(config, max_length=10)
    assert result.count == 2
    assert out["c"] == "short"
