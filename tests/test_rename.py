"""Tests for confpatch.rename."""

import pytest

from confpatch.rename import RenameError, RenameResult, rename_key, rename_keys


BASE = {"database": {"host": "localhost", "port": 5432}, "debug": True}


def test_rename_key_top_level():
    result = rename_key({"foo": 1, "bar": 2}, "foo", "baz")
    assert "baz" in result
    assert "foo" not in result
    assert result["baz"] == 1


def test_rename_key_nested():
    result = rename_key(BASE, "database.host", "hostname")
    assert "hostname" in result["database"]
    assert "host" not in result["database"]
    assert result["database"]["hostname"] == "localhost"


def test_rename_key_does_not_mutate_original():
    original = {"x": 10}
    rename_key(original, "x", "y")
    assert "x" in original


def test_rename_key_missing_raises():
    with pytest.raises(RenameError, match="not found"):
        rename_key({"a": 1}, "b", "c")


def test_rename_key_target_exists_raises():
    with pytest.raises(RenameError, match="already exists"):
        rename_key({"a": 1, "b": 2}, "a", "b")


def test_rename_key_parent_not_dict_raises():
    config = {"a": [1, 2, 3]}
    with pytest.raises(RenameError):
        rename_key(config, "a.0", "zero")


def test_rename_key_missing_parent_raises():
    with pytest.raises(RenameError, match="Parent path not found"):
        rename_key({"a": {"b": 1}}, "x.b", "c")


def test_rename_keys_multiple():
    config = {"a": 1, "b": 2, "c": 3}
    new_config, report = rename_keys(config, {"a": "alpha", "b": "beta"})
    assert "alpha" in new_config
    assert "beta" in new_config
    assert "a" not in new_config
    assert report.count == 2
    assert report.has_changes


def test_rename_keys_skip_missing():
    config = {"x": 10}
    new_config, report = rename_keys(config, {"x": "y", "missing": "gone"}, skip_missing=True)
    assert "y" in new_config
    assert "missing" in report.skipped


def test_rename_keys_no_skip_missing_raises():
    config = {"x": 10}
    with pytest.raises(RenameError):
        rename_keys(config, {"x": "y", "missing": "gone"}, skip_missing=False)


def test_rename_result_summary_contains_renamed():
    report = RenameResult(renamed=[("old", "new")], skipped=[])
    summary = report.summary()
    assert "old" in summary
    assert "new" in summary


def test_rename_result_no_changes():
    report = RenameResult()
    assert not report.has_changes
    assert report.count == 0
