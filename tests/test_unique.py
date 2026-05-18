"""Tests for confpatch.unique."""

import pytest
from confpatch.unique import UniqueError, UniqueResult, enforce_unique


@pytest.fixture
def config():
    return {
        "tags": ["a", "b", "a", "c", "b"],
        "ports": [8080, 9090, 8080],
        "name": "app",
        "nested": {
            "roles": ["admin", "user", "admin"],
            "level": 1,
        },
    }


def test_enforce_unique_returns_result(config):
    result = enforce_unique(config)
    assert isinstance(result, UniqueResult)


def test_enforce_unique_dedupes_top_level_list(config):
    result = enforce_unique(config)
    assert result.result["tags"] == ["a", "b", "c"]


def test_enforce_unique_dedupes_numeric_list(config):
    result = enforce_unique(config)
    assert result.result["ports"] == [8080, 9090]


def test_enforce_unique_dedupes_nested(config):
    result = enforce_unique(config)
    assert result.result["nested"]["roles"] == ["admin", "user"]


def test_enforce_unique_does_not_mutate_original(config):
    original_tags = list(config["tags"])
    enforce_unique(config)
    assert config["tags"] == original_tags


def test_enforce_unique_non_string_scalar_untouched(config):
    result = enforce_unique(config)
    assert result.result["name"] == "app"


def test_enforce_unique_has_changes_true(config):
    result = enforce_unique(config)
    assert result.has_changes() is True


def test_enforce_unique_has_changes_false():
    result = enforce_unique({"tags": ["a", "b", "c"]})
    assert result.has_changes() is False


def test_enforce_unique_count(config):
    result = enforce_unique(config)
    # tags: 2 removed, ports: 1 removed, nested.roles: 1 removed
    assert result.count() == 4


def test_enforce_unique_summary_no_changes():
    result = enforce_unique({"x": [1, 2, 3]})
    assert "No duplicate" in result.summary()


def test_enforce_unique_summary_with_changes(config):
    result = enforce_unique(config)
    summary = result.summary()
    assert "Removed" in summary
    assert "tags" in summary


def test_enforce_unique_specific_keys_only(config):
    result = enforce_unique(config, keys=["tags"])
    assert result.result["tags"] == ["a", "b", "c"]
    # ports should be untouched
    assert result.result["ports"] == [8080, 9090, 8080]


def test_enforce_unique_not_a_dict_raises():
    with pytest.raises(UniqueError):
        enforce_unique(["not", "a", "dict"])


def test_enforce_unique_empty_list_no_change():
    result = enforce_unique({"items": []})
    assert result.result["items"] == []
    assert not result.has_changes()


def test_enforce_unique_no_recursive():
    config = {"nested": {"roles": ["admin", "admin"]}, "tags": ["x", "x"]}
    result = enforce_unique(config, recursive=False)
    # top-level lists deduped, nested skipped
    assert result.result["tags"] == ["x"]
    assert result.result["nested"]["roles"] == ["admin", "admin"]
