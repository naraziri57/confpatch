"""Tests for confpatch.merge."""

import pytest

from confpatch.merge import MergeError, merge_configs, merge_into


# ---------------------------------------------------------------------------
# merge_configs – deep (default)
# ---------------------------------------------------------------------------

def test_deep_merge_adds_new_key():
    result = merge_configs({"a": 1}, {"b": 2})
    assert result == {"a": 1, "b": 2}


def test_deep_merge_overwrites_scalar():
    result = merge_configs({"a": 1}, {"a": 99})
    assert result["a"] == 99


def test_deep_merge_nested_dicts():
    base = {"db": {"host": "localhost", "port": 5432}}
    patch = {"db": {"port": 5433, "name": "mydb"}}
    result = merge_configs(base, patch)
    assert result["db"] == {"host": "localhost", "port": 5433, "name": "mydb"}


def test_deep_merge_does_not_mutate_base():
    base = {"a": {"x": 1}}
    patch = {"a": {"y": 2}}
    merge_configs(base, patch)
    assert base == {"a": {"x": 1}}


def test_deep_merge_list_overwrite_default():
    base = {"tags": ["a", "b"]}
    patch = {"tags": ["c"]}
    result = merge_configs(base, patch)
    assert result["tags"] == ["c"]


def test_deep_merge_list_append_when_flag_false():
    base = {"tags": ["a", "b"]}
    patch = {"tags": ["c"]}
    result = merge_configs(base, patch, overwrite_lists=False)
    assert result["tags"] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# merge_configs – shallow
# ---------------------------------------------------------------------------

def test_shallow_merge_does_not_recurse():
    base = {"db": {"host": "localhost", "port": 5432}}
    patch = {"db": {"port": 5433}}
    result = merge_configs(base, patch, strategy="shallow")
    # shallow: nested dict is fully replaced
    assert result["db"] == {"port": 5433}


def test_shallow_merge_adds_top_level_key():
    result = merge_configs({"a": 1}, {"b": 2}, strategy="shallow")
    assert result == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# merge_configs – replace
# ---------------------------------------------------------------------------

def test_replace_strategy_returns_patch_copy():
    base = {"a": 1, "b": 2}
    patch = {"c": 3}
    result = merge_configs(base, patch, strategy="replace")
    assert result == {"c": 3}


def test_replace_does_not_mutate_patch():
    patch = {"x": {"y": 1}}
    result = merge_configs({}, patch, strategy="replace")
    result["x"]["y"] = 999
    assert patch["x"]["y"] == 1


# ---------------------------------------------------------------------------
# Unknown strategy
# ---------------------------------------------------------------------------

def test_unknown_strategy_raises():
    with pytest.raises(MergeError, match="Unknown merge strategy"):
        merge_configs({}, {}, strategy="magic")


# ---------------------------------------------------------------------------
# merge_into – multiple patches
# ---------------------------------------------------------------------------

def test_merge_into_applies_patches_in_order():
    base = {"a": 1}
    result = merge_into(base, {"b": 2}, {"b": 99, "c": 3})
    assert result == {"a": 1, "b": 99, "c": 3}


def test_merge_into_no_patches_returns_copy():
    base = {"a": 1}
    result = merge_into(base)
    assert result == base
    assert result is not base
