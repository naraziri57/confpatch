"""Tests for confpatch.dedupe."""

import pytest

from confpatch.dedupe import (
    DedupeError,
    DedupeResult,
    _flatten_keys,
    dedupe_patch,
    find_duplicate_keys,
)


def test_flatten_keys_simple():
    data = {"a": 1, "b": 2}
    assert set(_flatten_keys(data)) == {"a", "b"}


def test_flatten_keys_nested():
    data = {"a": {"b": {"c": 1}}}
    keys = _flatten_keys(data)
    assert "a" in keys
    assert "a.b" in keys
    assert "a.b.c" in keys


def test_flatten_keys_mixed():
    data = {"x": 1, "y": {"z": 2}}
    keys = _flatten_keys(data)
    assert "x" in keys
    assert "y" in keys
    assert "y.z" in keys


def test_find_duplicate_keys_no_dupes():
    patch = {"a": 1, "b": 2, "c": 3}
    assert find_duplicate_keys(patch) == []


def test_find_duplicate_keys_not_dict_raises():
    with pytest.raises(DedupeError):
        find_duplicate_keys(["a", "b"])  # type: ignore


def test_find_duplicate_keys_empty():
    assert find_duplicate_keys({}) == []


def test_dedupe_patch_no_duplicates():
    patch = {"host": "localhost", "port": 8080}
    clean, result = dedupe_patch(patch)
    assert clean == patch
    assert not result.has_duplicates
    assert result.removed == 0


def test_dedupe_patch_returns_copy():
    patch = {"key": "value"}
    clean, _ = dedupe_patch(patch)
    clean["key"] = "modified"
    assert patch["key"] == "value"


def test_dedupe_patch_not_dict_raises():
    with pytest.raises(DedupeError):
        dedupe_patch("not a dict")  # type: ignore


def test_dedupe_patch_nested_no_dupes():
    patch = {"db": {"host": "localhost", "port": 5432}}
    clean, result = dedupe_patch(patch)
    assert clean == patch
    assert result.original_count == 3  # db, db.host, db.port


def test_dedupe_result_summary_no_dupes():
    result = DedupeResult()
    assert "No duplicate" in result.summary()


def test_dedupe_result_summary_with_dupes():
    result = DedupeResult(
        duplicates=["host"],
        removed=1,
        original_count=4,
        final_count=3,
    )
    summary = result.summary()
    assert "host" in summary
    assert "1" in summary


def test_dedupe_result_has_duplicates_false():
    result = DedupeResult()
    assert not result.has_duplicates


def test_dedupe_result_has_duplicates_true():
    result = DedupeResult(duplicates=["key"])
    assert result.has_duplicates
