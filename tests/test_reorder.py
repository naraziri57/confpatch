"""Tests for confpatch.reorder."""

import pytest
from confpatch.reorder import reorder_keys, ReorderError, ReorderResult


def test_reorder_basic_order():
    config = {"b": 2, "a": 1, "c": 3}
    result = reorder_keys(config, ["a", "b", "c"])
    assert list(result.reordered.keys()) == ["a", "b", "c"]
    assert result.has_changes()


def test_reorder_partial_order_appends_rest():
    config = {"b": 2, "a": 1, "c": 3}
    result = reorder_keys(config, ["c"])
    keys = list(result.reordered.keys())
    assert keys[0] == "c"
    assert set(keys) == {"a", "b", "c"}


def test_reorder_order_with_missing_keys_ignored():
    config = {"a": 1, "b": 2}
    result = reorder_keys(config, ["a", "z", "b"])
    assert list(result.reordered.keys()) == ["a", "b"]
    assert result.moved == ["a", "b"]


def test_reorder_does_not_mutate_original():
    config = {"b": 2, "a": 1}
    original_keys = list(config.keys())
    reorder_keys(config, ["a", "b"])
    assert list(config.keys()) == original_keys


def test_reorder_no_change_when_already_ordered():
    config = {"a": 1, "b": 2}
    result = reorder_keys(config, ["a", "b"])
    # moved still lists the keys, but order matches
    assert result.reordered == {"a": 1, "b": 2}


def test_reorder_with_scope():
    config = {"top": {"b": 2, "a": 1}, "other": "x"}
    result = reorder_keys(config, ["a", "b"], scope="top")
    assert list(result.reordered["top"].keys()) == ["a", "b"]
    assert result.reordered["other"] == "x"


def test_reorder_scope_not_found_raises():
    config = {"a": 1}
    with pytest.raises(ReorderError, match="not found"):
        reorder_keys(config, ["x"], scope="missing.path")


def test_reorder_scope_not_dict_raises():
    config = {"a": "scalar"}
    with pytest.raises(ReorderError):
        reorder_keys(config, ["x"], scope="a")


def test_reorder_config_not_dict_raises():
    with pytest.raises(ReorderError, match="dict"):
        reorder_keys(["a", "b"], ["a"])


def test_reorder_invalid_order_raises():
    with pytest.raises(ReorderError, match="list of strings"):
        reorder_keys({"a": 1}, "a")


def test_reorder_summary_with_changes():
    config = {"b": 2, "a": 1}
    result = reorder_keys(config, ["a", "b"])
    assert "Reordered" in result.summary()


def test_reorder_summary_no_changes():
    config = {"a": 1}
    result = reorder_keys(config, [])
    assert result.summary() == "No keys reordered."


def test_reorder_count():
    config = {"c": 3, "a": 1, "b": 2}
    result = reorder_keys(config, ["a", "b", "c"])
    assert result.count() == 3
