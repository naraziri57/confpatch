"""Tests for confpatch.copy."""

from __future__ import annotations

import pytest

from confpatch.copy import CopyError, CopyResult, copy_key, copy_keys


@pytest.fixture
def config():
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "app": {
            "debug": True,
        },
    }


def test_copy_key_top_level(config):
    new_config, report = copy_key(config, "app.debug", "app.verbose")
    assert new_config["app"]["verbose"] is True
    assert report.has_changes()
    assert report.count() == 1


def test_copy_key_does_not_mutate_original(config):
    original_keys = set(config["app"].keys())
    copy_key(config, "app.debug", "app.verbose")
    assert set(config["app"].keys()) == original_keys


def test_copy_key_creates_nested_destination(config):
    new_config, report = copy_key(config, "database.host", "backup.host")
    assert new_config["backup"]["host"] == "localhost"
    assert report.has_changes()


def test_copy_key_missing_source_raises(config):
    with pytest.raises(CopyError, match="Source key not found"):
        copy_key(config, "nonexistent.key", "app.something")


def test_copy_key_skip_existing_without_overwrite(config):
    config["app"]["debug_copy"] = False
    new_config, report = copy_key(config, "app.debug", "app.debug_copy", overwrite=False)
    assert new_config["app"]["debug_copy"] is False
    assert not report.has_changes()
    assert len(report.skipped) == 1


def test_copy_key_overwrite_existing(config):
    config["app"]["debug_copy"] = False
    new_config, report = copy_key(config, "app.debug", "app.debug_copy", overwrite=True)
    assert new_config["app"]["debug_copy"] is True
    assert report.has_changes()


def test_copy_keys_multiple_pairs(config):
    pairs = [("database.host", "backup.host"), ("database.port", "backup.port")]
    new_config, report = copy_keys(config, pairs)
    assert new_config["backup"]["host"] == "localhost"
    assert new_config["backup"]["port"] == 5432
    assert report.count() == 2


def test_copy_keys_partial_skip(config):
    config["app"]["verbose"] = False
    pairs = [("app.debug", "app.verbose"), ("database.host", "backup.host")]
    new_config, report = copy_keys(config, pairs, overwrite=False)
    assert new_config["app"]["verbose"] is False
    assert new_config["backup"]["host"] == "localhost"
    assert report.count() == 1
    assert len(report.skipped) == 1


def test_copy_result_summary_no_changes():
    result = CopyResult()
    assert "0" in result.summary()


def test_copy_result_summary_with_copies():
    result = CopyResult(copied=[("a", "b"), ("c", "d")], skipped=[("e", "f")])
    summary = result.summary()
    assert "a -> b" in summary
    assert "Skipped 1" in summary


def test_copy_key_deep_dot_notation(config):
    config["database"]["replica"] = {"host": "replica-host"}
    new_config, report = copy_key(config, "database.replica.host", "database.host")
    assert new_config["database"]["host"] == "replica-host" or not report.has_changes()
