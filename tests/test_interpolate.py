"""Tests for confpatch.interpolate."""

from __future__ import annotations

import pytest

from confpatch.interpolate import (
    InterpolateError,
    InterpolateResult,
    interpolate_config,
    _get_nested,
    _interpolate_string,
)


def test_get_nested_top_level():
    config = {"host": "localhost"}
    assert _get_nested(config, "host") == "localhost"


def test_get_nested_dotted():
    config = {"db": {"host": "127.0.0.1"}}
    assert _get_nested(config, "db.host") == "127.0.0.1"


def test_get_nested_missing_raises():
    config = {"a": 1}
    with pytest.raises(InterpolateError, match="not found"):
        _get_nested(config, "b")


def test_interpolate_string_simple():
    config = {"host": "localhost"}
    result, resolved = _interpolate_string("connect to ${host}", config)
    assert result == "connect to localhost"
    assert "host" in resolved


def test_interpolate_string_multiple_refs():
    config = {"host": "db", "port": "5432"}
    result, resolved = _interpolate_string("${host}:${port}", config)
    assert result == "db:5432"
    assert len(resolved) == 2


def test_interpolate_string_missing_ref_raises():
    config = {}
    with pytest.raises(InterpolateError):
        _interpolate_string("${missing}", config)


def test_interpolate_config_no_refs():
    config = {"key": "value", "num": 42}
    result = interpolate_config(config)
    assert not result.has_changes()
    assert result.count() == 0
    assert result.result == config


def test_interpolate_config_single_ref():
    config = {"base_url": "https://example.com", "api": "${base_url}/v1"}
    result = interpolate_config(config)
    assert result.result["api"] == "https://example.com/v1"
    assert result.has_changes()


def test_interpolate_config_nested_ref():
    config = {
        "defaults": {"timeout": 30},
        "service": {"timeout": "${defaults.timeout}"},
    }
    result = interpolate_config(config)
    assert result.result["service"]["timeout"] == "30"


def test_interpolate_config_does_not_mutate_original():
    config = {"host": "localhost", "dsn": "${host}/db"}
    original_dsn = config["dsn"]
    interpolate_config(config)
    assert config["dsn"] == original_dsn


def test_interpolate_config_list_values():
    config = {"prefix": "app", "tags": ["${prefix}-web", "${prefix}-worker"]}
    result = interpolate_config(config)
    assert result.result["tags"] == ["app-web", "app-worker"]


def test_interpolate_config_non_dict_raises():
    with pytest.raises(InterpolateError):
        interpolate_config(["not", "a", "dict"])  # type: ignore


def test_interpolate_result_summary_no_changes():
    r = InterpolateResult(original={}, result={}, resolved=[])
    assert "No" in r.summary()


def test_interpolate_result_summary_with_changes():
    r = InterpolateResult(original={}, result={}, resolved=["host", "port"])
    assert "2" in r.summary()
    assert "host" in r.summary()
