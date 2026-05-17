"""Tests for confpatch.defaults."""

from __future__ import annotations

import pytest

from confpatch.defaults import (
    DefaultsError,
    DefaultsResult,
    apply_defaults,
)


# --- apply_defaults ---

def test_apply_defaults_adds_missing_key():
    config = {"host": "localhost"}
    new_cfg, result = apply_defaults(config, {"port": 8080})
    assert new_cfg["port"] == 8080
    assert result.applied == {"port": 8080}
    assert result.skipped == {}


def test_apply_defaults_skips_existing_key():
    config = {"port": 9000}
    new_cfg, result = apply_defaults(config, {"port": 8080})
    assert new_cfg["port"] == 9000
    assert "port" in result.skipped
    assert result.applied == {}


def test_apply_defaults_overwrites_null_by_default():
    config = {"port": None}
    new_cfg, result = apply_defaults(config, {"port": 8080})
    assert new_cfg["port"] == 8080
    assert result.applied == {"port": 8080}


def test_apply_defaults_skips_null_when_disabled():
    config = {"port": None}
    new_cfg, result = apply_defaults(config, {"port": 8080}, overwrite_null=False)
    assert new_cfg["port"] is None
    assert "port" in result.skipped
    assert result.applied == {}


def test_apply_defaults_dot_notation_creates_nested():
    config = {}
    new_cfg, result = apply_defaults(config, {"database.host": "localhost"})
    assert new_cfg["database"]["host"] == "localhost"
    assert result.applied == {"database.host": "localhost"}


def test_apply_defaults_dot_notation_skips_existing_nested():
    config = {"database": {"host": "prod-db"}}
    new_cfg, result = apply_defaults(config, {"database.host": "localhost"})
    assert new_cfg["database"]["host"] == "prod-db"
    assert "database.host" in result.skipped


def test_apply_defaults_does_not_mutate_original():
    config = {"a": 1}
    apply_defaults(config, {"b": 2})
    assert "b" not in config


def test_apply_defaults_multiple_keys():
    config = {"a": 1}
    new_cfg, result = apply_defaults(config, {"a": 99, "b": 2, "c": 3})
    assert new_cfg["a"] == 1
    assert new_cfg["b"] == 2
    assert new_cfg["c"] == 3
    assert result.count() == 2


def test_apply_defaults_non_dict_config_raises():
    with pytest.raises(DefaultsError):
        apply_defaults(["not", "a", "dict"], {"key": "val"})


def test_apply_defaults_non_dict_defaults_raises():
    with pytest.raises(DefaultsError):
        apply_defaults({}, ["not", "a", "dict"])


# --- DefaultsResult ---

def test_result_has_changes_true():
    r = DefaultsResult(applied={"x": 1})
    assert r.has_changes() is True


def test_result_has_changes_false():
    r = DefaultsResult()
    assert r.has_changes() is False


def test_result_count():
    r = DefaultsResult(applied={"a": 1, "b": 2})
    assert r.count() == 2


def test_result_summary_no_changes():
    r = DefaultsResult()
    assert "No defaults" in r.summary()


def test_result_summary_with_changes():
    r = DefaultsResult(applied={"port": 8080})
    summary = r.summary()
    assert "port" in summary
    assert "8080" in summary
