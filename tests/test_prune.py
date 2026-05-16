"""Tests for confpatch.prune."""
import pytest
from confpatch.prune import prune_config, PruneResult, PruneError


def test_prune_no_nulls_returns_copy():
    config = {"a": 1, "b": "hello"}
    result = prune_config(config)
    assert result.pruned == config
    assert result.removed_keys == []
    assert not result.has_removals()


def test_prune_removes_null_top_level():
    config = {"a": 1, "b": None}
    result = prune_config(config)
    assert result.pruned == {"a": 1}
    assert "b" in result.removed_keys


def test_prune_removes_null_nested():
    config = {"outer": {"x": 10, "y": None}}
    result = prune_config(config)
    assert result.pruned == {"outer": {"x": 10}}
    assert "outer.y" in result.removed_keys


def test_prune_does_not_mutate_original():
    config = {"a": None, "b": 2}
    prune_config(config)
    assert config == {"a": None, "b": 2}


def test_prune_empty_false_keeps_empty_strings():
    config = {"a": "", "b": "hello"}
    result = prune_config(config, prune_empty=False)
    assert result.pruned == {"a": "", "b": "hello"}
    assert result.removed_keys == []


def test_prune_empty_true_removes_empty_string():
    config = {"a": "", "b": "hello"}
    result = prune_config(config, prune_empty=True)
    assert result.pruned == {"b": "hello"}
    assert "a" in result.removed_keys


def test_prune_empty_true_removes_empty_list():
    config = {"items": [], "name": "foo"}
    result = prune_config(config, prune_empty=True)
    assert result.pruned == {"name": "foo"}
    assert "items" in result.removed_keys


def test_prune_count_and_summary():
    config = {"a": None, "b": None, "c": 3}
    result = prune_config(config)
    assert result.count() == 2
    assert "Pruned 2 key(s)" in result.summary()


def test_prune_summary_no_removals():
    config = {"a": 1}
    result = prune_config(config)
    assert result.summary() == "No keys pruned."


def test_prune_raises_on_non_dict():
    with pytest.raises(PruneError):
        prune_config(["not", "a", "dict"])


def test_prune_multiple_nulls_nested():
    config = {"db": {"host": "localhost", "password": None, "port": None}}
    result = prune_config(config)
    assert result.pruned == {"db": {"host": "localhost"}}
    assert "db.password" in result.removed_keys
    assert "db.port" in result.removed_keys
