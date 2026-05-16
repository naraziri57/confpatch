"""Tests for confpatch.flatten."""

import pytest
from confpatch.flatten import (
    flatten_config,
    unflatten_config,
    FlattenError,
    FlattenResult,
)


def test_flatten_simple():
    config = {"a": 1, "b": 2}
    result = flatten_config(config)
    assert result.flat == {"a": 1, "b": 2}


def test_flatten_nested():
    config = {"database": {"host": "localhost", "port": 5432}}
    result = flatten_config(config)
    assert result.flat == {"database.host": "localhost", "database.port": 5432}


def test_flatten_deep():
    config = {"a": {"b": {"c": 42}}}
    result = flatten_config(config)
    assert result.flat == {"a.b.c": 42}


def test_flatten_mixed():
    config = {"x": 1, "y": {"z": 2}}
    result = flatten_config(config)
    assert result.flat == {"x": 1, "y.z": 2}


def test_flatten_custom_sep():
    config = {"a": {"b": 1}}
    result = flatten_config(config, sep="/")
    assert result.flat == {"a/b": 1}


def test_flatten_returns_flatten_result():
    config = {"a": {"b": 1}, "c": 2}
    result = flatten_config(config)
    assert isinstance(result, FlattenResult)
    assert result.original_keys == 2
    assert result.flat_keys == 2


def test_flatten_not_dict_raises():
    with pytest.raises(FlattenError):
        flatten_config(["not", "a", "dict"])


def test_flatten_summary():
    config = {"a": {"b": 1}}
    result = flatten_config(config)
    s = result.summary()
    assert "1" in s
    assert "dot-notation" in s


def test_unflatten_simple():
    flat = {"a": 1, "b": 2}
    result = unflatten_config(flat)
    assert result == {"a": 1, "b": 2}


def test_unflatten_nested():
    flat = {"database.host": "localhost", "database.port": 5432}
    result = unflatten_config(flat)
    assert result == {"database": {"host": "localhost", "port": 5432}}


def test_unflatten_deep():
    flat = {"a.b.c": 42}
    result = unflatten_config(flat)
    assert result == {"a": {"b": {"c": 42}}}


def test_unflatten_custom_sep():
    flat = {"a/b": 1}
    result = unflatten_config(flat, sep="/")
    assert result == {"a": {"b": 1}}


def test_unflatten_not_dict_raises():
    with pytest.raises(FlattenError):
        unflatten_config("not a dict")


def test_flatten_unflatten_roundtrip():
    config = {"server": {"host": "0.0.0.0", "port": 8080}, "debug": True}
    result = flatten_config(config)
    restored = unflatten_config(result.flat)
    assert restored == config
