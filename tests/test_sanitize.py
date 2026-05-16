"""Tests for confpatch.sanitize."""

import pytest
from confpatch.sanitize import sanitize_config, SanitizeError, SanitizeResult


def test_sanitize_no_changes_on_clean_config():
    config = {"host": "localhost", "port": 8080}
    result = sanitize_config(config)
    assert result.cleaned == config
    assert not result.has_changes()


def test_sanitize_strips_whitespace_by_default():
    config = {"name": "  hello  ", "value": "world"}
    result = sanitize_config(config)
    assert result.cleaned["name"] == "hello"
    assert result.cleaned["value"] == "world"
    assert result.has_changes()
    assert result.count() == 1


def test_sanitize_no_strip_when_disabled():
    config = {"name": "  hello  "}
    result = sanitize_config(config, strip=False)
    assert result.cleaned["name"] == "  hello  "
    assert not result.has_changes()


def test_sanitize_lowercase():
    config = {"env": "PRODUCTION", "level": "DEBUG"}
    result = sanitize_config(config, lowercase=True)
    assert result.cleaned["env"] == "production"
    assert result.cleaned["level"] == "debug"
    assert result.count() == 2


def test_sanitize_collapse_whitespace():
    config = {"message": "hello   world  foo"}
    result = sanitize_config(config, collapse=True)
    assert result.cleaned["message"] == "hello world foo"
    assert result.has_changes()


def test_sanitize_non_string_passthrough():
    config = {"count": 42, "flag": True, "ratio": 3.14}
    result = sanitize_config(config)
    assert result.cleaned == config
    assert not result.has_changes()


def test_sanitize_nested_dict():
    config = {"db": {"host": "  localhost  ", "port": 5432}}
    result = sanitize_config(config)
    assert result.cleaned["db"]["host"] == "localhost"
    assert result.cleaned["db"]["port"] == 5432
    assert result.count() == 1
    assert result.changes[0][0] == "db.host"


def test_sanitize_does_not_mutate_original():
    config = {"name": "  test  "}
    original = dict(config)
    sanitize_config(config)
    assert config == original


def test_sanitize_raises_on_non_dict():
    with pytest.raises(SanitizeError):
        sanitize_config(["not", "a", "dict"])


def test_sanitize_summary_no_changes():
    config = {"key": "value"}
    result = sanitize_config(config)
    assert "No sanitization" in result.summary()


def test_sanitize_summary_with_changes():
    config = {"name": "  hello  "}
    result = sanitize_config(config)
    summary = result.summary()
    assert "Sanitized" in summary
    assert "name" in summary


def test_sanitize_strip_and_lowercase_combined():
    config = {"tag": "  HELLO  "}
    result = sanitize_config(config, strip=True, lowercase=True)
    assert result.cleaned["tag"] == "hello"
    assert result.count() == 1
