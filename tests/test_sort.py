"""Tests for confpatch.sort."""

import pytest

from confpatch.sort import SortError, SortResult, sort_config


def test_sort_already_sorted_no_changes():
    config = {"a": 1, "b": 2, "c": 3}
    result = sort_config(config)
    assert result.sorted_config == {"a": 1, "b": 2, "c": 3}
    assert not result.has_changes()


def test_sort_basic_reorder():
    config = {"z": 1, "a": 2, "m": 3}
    result = sort_config(config)
    assert list(result.sorted_config.keys()) == ["a", "m", "z"]
    assert result.has_changes()


def test_sort_does_not_mutate_original():
    config = {"z": 1, "a": 2}
    original_keys = list(config.keys())
    sort_config(config)
    assert list(config.keys()) == original_keys


def test_sort_reverse():
    config = {"a": 1, "b": 2, "c": 3}
    result = sort_config(config, reverse=True)
    assert list(result.sorted_config.keys()) == ["c", "b", "a"]


def test_sort_recursive_nested():
    config = {"outer": {"z": 1, "a": 2}}
    result = sort_config(config, recursive=True)
    assert list(result.sorted_config["outer"].keys()) == ["a", "z"]


def test_sort_non_recursive_leaves_nested_unsorted():
    config = {"outer": {"z": 1, "a": 2}}
    result = sort_config(config, recursive=False)
    assert list(result.sorted_config["outer"].keys()) == ["z", "a"]


def test_sort_non_dict_raises():
    with pytest.raises(SortError, match="Expected a dict"):
        sort_config(["not", "a", "dict"])  # type: ignore


def test_sort_returns_sort_result_instance():
    result = sort_config({"b": 1, "a": 2})
    assert isinstance(result, SortResult)


def test_sort_count_reflects_changed_keys():
    config = {"z": 1, "a": 2, "m": 3}
    result = sort_config(config)
    assert result.count() > 0


def test_sort_summary_no_changes():
    config = {"a": 1, "b": 2}
    result = sort_config(config)
    assert "No keys" in result.summary()


def test_sort_summary_with_changes():
    config = {"z": 1, "a": 2}
    result = sort_config(config)
    assert "Reordered" in result.summary()


def test_sort_empty_dict():
    result = sort_config({})
    assert result.sorted_config == {}
    assert not result.has_changes()


def test_sort_preserves_values():
    config = {"z": [1, 2, 3], "a": {"nested": True}}
    result = sort_config(config)
    assert result.sorted_config["a"] == {"nested": True}
    assert result.sorted_config["z"] == [1, 2, 3]
