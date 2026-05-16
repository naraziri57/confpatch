"""Tests for confpatch.promote."""
from __future__ import annotations

import pytest

from confpatch.promote import PromoteError, PromoteResult, promote_key


@pytest.fixture
def config():
    return {
        "app": {
            "host": "localhost",
            "port": 8080,
        },
        "debug": True,
    }


def test_promote_key_returns_result(config):
    result = promote_key(config, "app")
    assert isinstance(result, PromoteResult)


def test_promote_key_moves_nested_keys(config):
    result = promote_key(config, "app")
    assert result.config["host"] == "localhost"
    assert result.config["port"] == 8080


def test_promote_key_keeps_other_keys(config):
    result = promote_key(config, "app")
    assert result.config["debug"] is True


def test_promote_key_does_not_mutate_original(config):
    original = dict(config)
    promote_key(config, "app")
    assert config == original


def test_promote_key_remove_source(config):
    result = promote_key(config, "app", remove_source=True)
    assert "app" not in result.config
    assert result.config["host"] == "localhost"


def test_promote_key_keeps_source_by_default(config):
    result = promote_key(config, "app")
    assert "app" in result.config


def test_promote_key_conflict_raises(config):
    config["host"] = "existing"
    with pytest.raises(PromoteError, match="already exist"):
        promote_key(config, "app")


def test_promote_key_overwrite_resolves_conflict(config):
    config["host"] = "existing"
    result = promote_key(config, "app", overwrite=True)
    assert result.config["host"] == "localhost"


def test_promote_key_missing_path_raises(config):
    with pytest.raises(PromoteError, match="not found"):
        promote_key(config, "nonexistent")


def test_promote_key_non_dict_raises(config):
    with pytest.raises(PromoteError, match="not a dict"):
        promote_key(config, "debug")


def test_promote_key_dot_notation():
    config = {"a": {"b": {"x": 1, "y": 2}}}
    result = promote_key(config, "a.b")
    assert result.config["x"] == 1
    assert result.config["y"] == 2


def test_promote_result_has_changes(config):
    result = promote_key(config, "app")
    assert result.has_changes()


def test_promote_result_count(config):
    result = promote_key(config, "app")
    assert result.count() == 2


def test_promote_result_summary(config):
    result = promote_key(config, "app")
    assert "app" in result.summary()
    assert "2" in result.summary()


def test_promote_result_source_path(config):
    result = promote_key(config, "app")
    assert result.source_path == "app"
