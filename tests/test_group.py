"""Tests for confpatch.group."""

import pytest

from confpatch.group import GroupError, GroupResult, group_keys


@pytest.fixture
def config():
    return {
        "host": "localhost",
        "port": 5432,
        "user": "admin",
        "password": "secret",
        "debug": True,
    }


def test_group_keys_basic(config):
    result = group_keys(config, keys=["host", "port"], group="database")
    assert isinstance(result, GroupResult)
    assert result.grouped["database"]["host"] == "localhost"
    assert result.grouped["database"]["port"] == 5432
    assert "host" not in result.grouped
    assert "port" not in result.grouped


def test_group_keys_does_not_mutate_original(config):
    original_copy = dict(config)
    group_keys(config, keys=["host"], group="db")
    assert config == original_copy


def test_group_keys_has_changes(config):
    result = group_keys(config, keys=["host"], group="db")
    assert result.has_changes()
    assert result.count() == 1


def test_group_keys_summary(config):
    result = group_keys(config, keys=["host", "port"], group="db")
    s = result.summary()
    assert "2" in s
    assert "host" in s or "port" in s


def test_group_keys_nested_group(config):
    result = group_keys(config, keys=["user", "password"], group="database.credentials")
    assert result.grouped["database"]["credentials"]["user"] == "admin"
    assert result.grouped["database"]["credentials"]["password"] == "secret"


def test_group_keys_missing_key_raises(config):
    with pytest.raises(GroupError, match="not found"):
        group_keys(config, keys=["nonexistent"], group="section")


def test_group_keys_empty_keys_raises(config):
    with pytest.raises(GroupError, match="No keys"):
        group_keys(config, keys=[], group="section")


def test_group_keys_empty_group_raises(config):
    with pytest.raises(GroupError, match="Group path"):
        group_keys(config, keys=["host"], group="")


def test_group_keys_not_dict_raises():
    with pytest.raises(GroupError, match="must be a dict"):
        group_keys(["a", "b"], keys=["a"], group="section")


def test_group_keys_duplicate_in_group_raises(config):
    # First group
    result = group_keys(config, keys=["host"], group="db")
    # Try again without overwrite
    with pytest.raises(GroupError, match="already exists"):
        group_keys(result.grouped, keys=["debug"], group="db")
    # But debug is not in db yet — put host back scenario: key collision
    result2 = group_keys(config, keys=["host"], group="db")
    with pytest.raises(GroupError, match="already exists"):
        group_keys(result2.grouped, keys=["debug"], group="db")


def test_group_keys_overwrite(config):
    result1 = group_keys(config, keys=["host"], group="db")
    # Add another key to db.host by overwrite
    result2 = group_keys(result1.grouped, keys=["debug"], group="db", overwrite=True)
    assert result2.grouped["db"]["debug"] is True


def test_group_no_changes_summary():
    # Simulate a result with no moves
    r = GroupResult(original={}, grouped={}, moved=[])
    assert not r.has_changes()
    assert "No keys" in r.summary()
