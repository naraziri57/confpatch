"""Tests for confpatch.clamp."""

import pytest

from confpatch.clamp import ClampError, ClampResult, clamp_config


def test_clamp_no_changes_when_in_range():
    config = {"a": 5, "b": 10}
    result = clamp_config(config, min_val=0, max_val=100)
    assert result.clamped == {"a": 5, "b": 10}
    assert not result.has_changes()


def test_clamp_below_min():
    config = {"x": -5}
    result = clamp_config(config, min_val=0)
    assert result.clamped["x"] == 0
    assert result.has_changes()


def test_clamp_above_max():
    config = {"x": 200}
    result = clamp_config(config, max_val=100)
    assert result.clamped["x"] == 100
    assert result.has_changes()


def test_clamp_preserves_type_int():
    config = {"x": 200}
    result = clamp_config(config, max_val=100)
    assert isinstance(result.clamped["x"], int)


def test_clamp_preserves_type_float():
    config = {"x": 3.14}
    result = clamp_config(config, max_val=3.0)
    assert isinstance(result.clamped["x"], float)


def test_clamp_non_numeric_passthrough():
    config = {"name": "alice", "score": 200}
    result = clamp_config(config, max_val=100)
    assert result.clamped["name"] == "alice"
    assert result.clamped["score"] == 100


def test_clamp_does_not_mutate_original():
    config = {"x": 500}
    clamp_config(config, max_val=100)
    assert config["x"] == 500


def test_clamp_nested_dict():
    config = {"server": {"timeout": 9999, "retries": 1}}
    result = clamp_config(config, max_val=100)
    assert result.clamped["server"]["timeout"] == 100
    assert result.clamped["server"]["retries"] == 1


def test_clamp_specific_keys_only():
    config = {"a": 500, "b": 500}
    result = clamp_config(config, max_val=100, keys=["a"])
    assert result.clamped["a"] == 100
    assert result.clamped["b"] == 500


def test_clamp_count():
    config = {"a": 200, "b": -10, "c": 50}
    result = clamp_config(config, min_val=0, max_val=100)
    assert result.count() == 2


def test_clamp_summary_no_changes():
    config = {"a": 5}
    result = clamp_config(config, min_val=0, max_val=10)
    assert "No values clamped" in result.summary()


def test_clamp_summary_with_changes():
    config = {"a": 200}
    result = clamp_config(config, max_val=100)
    s = result.summary()
    assert "Clamped" in s
    assert "200" in s
    assert "100" in s


def test_clamp_invalid_range_raises():
    with pytest.raises(ClampError, match="min_val"):
        clamp_config({"x": 5}, min_val=10, max_val=5)


def test_clamp_non_dict_raises():
    with pytest.raises(ClampError):
        clamp_config([1, 2, 3], min_val=0)
