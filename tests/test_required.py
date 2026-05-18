"""Tests for confpatch.required."""

import pytest

from confpatch.required import RequiredError, RequiredResult, check_required


@pytest.fixture
def config():
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "app": {
            "debug": False,
        },
        "version": "1.0",
    }


def test_check_required_all_present(config):
    result = check_required(config, ["version", "database.host", "app.debug"])
    assert not result.has_missing()
    assert result.count() == 0


def test_check_required_missing_top_level(config):
    result = check_required(config, ["version", "missing_key"])
    assert result.has_missing()
    assert "missing_key" in result.missing


def test_check_required_missing_nested(config):
    result = check_required(config, ["database.password"])
    assert result.has_missing()
    assert "database.password" in result.missing


def test_check_required_multiple_missing(config):
    result = check_required(config, ["a", "b", "c"])
    assert result.count() == 3
    assert set(result.missing) == {"a", "b", "c"}


def test_check_required_empty_keys(config):
    result = check_required(config, [])
    assert not result.has_missing()
    assert result.checked == []


def test_check_required_non_dict_raises():
    with pytest.raises(RequiredError):
        check_required(["not", "a", "dict"], ["key"])


def test_check_required_checked_list_populated(config):
    keys = ["version", "database.host"]
    result = check_required(config, keys)
    assert result.checked == keys


def test_summary_all_present(config):
    result = check_required(config, ["version", "database.host"])
    assert "All 2" in result.summary()
    assert "present" in result.summary()


def test_summary_with_missing(config):
    result = check_required(config, ["version", "missing"])
    assert "1 required key(s) missing" in result.summary()
    assert "missing" in result.summary()


def test_check_required_deep_nested():
    config = {"a": {"b": {"c": 42}}}
    result = check_required(config, ["a.b.c"])
    assert not result.has_missing()


def test_check_required_deep_nested_missing():
    config = {"a": {"b": {}}}
    result = check_required(config, ["a.b.c"])
    assert result.has_missing()
    assert "a.b.c" in result.missing
