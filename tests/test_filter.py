"""Tests for confpatch.filter module."""

import pytest

from confpatch.filter import FilterError, filter_keys, filter_patch


# --- filter_keys ---

def test_filter_keys_no_filters_returns_copy():
    data = {"a": 1, "b": 2}
    result = filter_keys(data)
    assert result == {"a": 1, "b": 2}
    assert result is not data


def test_filter_keys_include_exact():
    data = {"a": 1, "b": 2, "c": 3}
    result = filter_keys(data, include=["a", "c"])
    assert result == {"a": 1, "c": 3}


def test_filter_keys_include_glob():
    data = {"db_host": "x", "db_port": 5432, "app_name": "y"}
    result = filter_keys(data, include=["db_*"])
    assert result == {"db_host": "x", "db_port": 5432}


def test_filter_keys_exclude_exact():
    data = {"a": 1, "b": 2, "c": 3}
    result = filter_keys(data, exclude=["b"])
    assert result == {"a": 1, "c": 3}


def test_filter_keys_exclude_glob():
    data = {"tmp_a": 1, "tmp_b": 2, "keep": 3}
    result = filter_keys(data, exclude=["tmp_*"])
    assert result == {"keep": 3}


def test_filter_keys_include_and_exclude():
    data = {"db_host": "x", "db_pass": "secret", "app": "y"}
    result = filter_keys(data, include=["db_*"], exclude=["db_pass"])
    assert result == {"db_host": "x"}


def test_filter_keys_not_a_dict_raises():
    with pytest.raises(FilterError, match="Expected a dict"):
        filter_keys(["a", "b"])  # type: ignore


def test_filter_keys_invalid_include_type_raises():
    with pytest.raises(FilterError, match="include must be a list"):
        filter_keys({"a": 1}, include="a")  # type: ignore


def test_filter_keys_invalid_exclude_type_raises():
    with pytest.raises(FilterError, match="exclude must be a list"):
        filter_keys({"a": 1}, exclude="a")  # type: ignore


def test_filter_keys_empty_data():
    assert filter_keys({}) == {}


# --- filter_patch ---

def test_filter_patch_shallow():
    patch = {"host": "localhost", "port": 8080, "debug": True}
    result = filter_patch(patch, exclude=["debug"])
    assert result == {"host": "localhost", "port": 8080}


def test_filter_patch_recursive_applies_to_nested():
    patch = {
        "database": {"host": "db", "password": "s3cr3t"},
        "app": {"host": "web", "password": "abc"},
    }
    result = filter_patch(patch, exclude=["password"], recursive=True)
    assert result == {
        "database": {"host": "db"},
        "app": {"host": "web"},
    }


def test_filter_patch_recursive_false_does_not_touch_nested():
    patch = {
        "database": {"host": "db", "password": "s3cr3t"},
    }
    result = filter_patch(patch, exclude=["password"], recursive=False)
    # top-level key 'database' not excluded, nested untouched
    assert result == {"database": {"host": "db", "password": "s3cr3t"}}


def test_filter_patch_include_top_level_glob():
    patch = {"db_host": "x", "db_port": 1, "secret": "y"}
    result = filter_patch(patch, include=["db_*"])
    assert "secret" not in result
    assert result["db_host"] == "x"
