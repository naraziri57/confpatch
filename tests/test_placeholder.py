"""Tests for confpatch.placeholder."""

import pytest

from confpatch.placeholder import (
    PlaceholderError,
    PlaceholderResult,
    resolve_placeholders,
    _resolve_string,
)


def test_resolve_string_simple():
    assert _resolve_string("hello <name>", {"name": "world"}, strict=True) == "hello world"


def test_resolve_string_multiple_tokens():
    result = _resolve_string("<first> <last>", {"first": "Ada", "last": "Lovelace"}, strict=True)
    assert result == "Ada Lovelace"


def test_resolve_string_missing_strict_raises():
    with pytest.raises(PlaceholderError, match="No value provided"):
        _resolve_string("<missing>", {}, strict=True)


def test_resolve_string_missing_non_strict_keeps_token():
    result = _resolve_string("<missing>", {}, strict=False)
    assert result == "<missing>"


def test_resolve_placeholders_top_level_key():
    config = {"greeting": "Hello, <name>!"}
    result = resolve_placeholders(config, {"name": "Alice"})
    assert result.resolved["greeting"] == "Hello, Alice!"
    assert result.has_changes()
    assert result.count() == 1


def test_resolve_placeholders_no_changes():
    config = {"greeting": "Hello, world!"}
    result = resolve_placeholders(config, {"name": "Alice"})
    assert not result.has_changes()
    assert result.resolved == config


def test_resolve_placeholders_nested_dict():
    config = {"db": {"host": "<db_host>", "port": 5432}}
    result = resolve_placeholders(config, {"db_host": "localhost"})
    assert result.resolved["db"]["host"] == "localhost"
    assert result.resolved["db"]["port"] == 5432


def test_resolve_placeholders_list_values():
    config = {"hosts": ["<h1>", "<h2>"]}
    result = resolve_placeholders(config, {"h1": "alpha", "h2": "beta"})
    assert result.resolved["hosts"] == ["alpha", "beta"]


def test_resolve_placeholders_non_string_passthrough():
    config = {"count": 42, "enabled": True}
    result = resolve_placeholders(config, {})
    assert result.resolved["count"] == 42
    assert result.resolved["enabled"] is True
    assert not result.has_changes()


def test_resolve_placeholders_limit_to_keys():
    config = {"a": "<token>", "b": "<token>"}
    result = resolve_placeholders(config, {"token": "X"}, keys=["a"])
    assert result.resolved["a"] == "X"
    assert result.resolved["b"] == "<token>"  # untouched


def test_resolve_placeholders_does_not_mutate_original():
    config = {"msg": "<greeting> world"}
    original_copy = dict(config)
    resolve_placeholders(config, {"greeting": "hi"})
    assert config == original_copy


def test_resolve_placeholders_not_dict_raises():
    with pytest.raises(PlaceholderError, match="Config must be a dict"):
        resolve_placeholders(["not", "a", "dict"], {})


def test_summary_with_changes():
    config = {"url": "https://<host>/api"}
    result = resolve_placeholders(config, {"host": "example.com"})
    s = result.summary()
    assert "url" in s
    assert "example.com" in s


def test_summary_no_changes():
    config = {"key": "value"}
    result = resolve_placeholders(config, {})
    assert "No placeholder" in result.summary()
